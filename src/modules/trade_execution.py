"""Centralized trade execution with risk checks and persistence."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from types import SimpleNamespace
from typing import Any, Dict, Optional

from src.modules.database import DatabaseManager
from src.modules.wallet_manager import UserWalletManager
from src.modules.jupiter_client import JupiterClient
from src.modules.elite_protection import EliteProtectionSystem
from src.modules.monitoring import BotMonitor
from src.modules.social_trading import (
    SocialTradingMarketplace,
    RewardSystem,
    REWARD_POINTS,
)

logger = logging.getLogger(__name__)


class TradeExecutionError(Exception):
    """Raised when a trade cannot be executed."""


class TradeExecutionService:
    """Handles manual and automated trade execution with risk controls."""

    SOL_MINT = "So11111111111111111111111111111111111111112"

    def __init__(
        self,
        db: DatabaseManager,
        wallet_manager: UserWalletManager,
        jupiter: JupiterClient,
        protection: Optional[EliteProtectionSystem] = None,
        monitor: Optional[BotMonitor] = None,
        social_marketplace: Optional[SocialTradingMarketplace] = None,
        rewards: Optional[RewardSystem] = None,
    ) -> None:
        self.db = db
        self.wallet_manager = wallet_manager
        self.jupiter = jupiter
        self.protection = protection
        self.monitor = monitor
        self.social_marketplace = social_marketplace
        self.rewards = rewards

    async def execute_buy(
        self,
        user_id: int,
        token_mint: str,
        amount_sol: float,
        *,
        token_symbol: Optional[str] = None,
        reason: str = "manual",
        context: str = "manual",
        execution_mode: str = "standard",
        priority_fee_lamports: Optional[int] = None,
        tip_lamports: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Execute a SOL -> token swap with safety and persistence."""

        if amount_sol <= 0:
            return {"success": False, "error": "Trade amount must be positive"}

        settings = await self._get_user_settings(user_id)

        if amount_sol > settings.max_trade_size_sol:
            return {
                "success": False,
                "error": (
                    f"Trade exceeds max size ({settings.max_trade_size_sol:.2f} SOL)."
                ),
            }

        daily_pnl = await self.db.get_daily_pnl(user_id)
        if daily_pnl <= -settings.daily_loss_limit_sol:
            return {
                "success": False,
                "error": "Daily loss limit reached. Trading paused until tomorrow.",
            }

        balance = await self.wallet_manager.get_user_balance(user_id)
        if balance < amount_sol:
            return {
                "success": False,
                "error": (
                    f"Insufficient balance. Available {balance:.4f} SOL, required {amount_sol:.4f} SOL."
                ),
            }

        if self.protection and settings.check_honeypots:
            safety = await self.protection.comprehensive_token_check(token_mint)
            if not safety.get("is_safe", False):
                return {
                    "success": False,
                    "error": "Token failed safety checks. Trade blocked.",
                    "details": safety,
                }
            liquidity = safety.get("details", {}).get("liquidity_usd", 0)
            if liquidity < settings.min_liquidity_usd:
                return {
                    "success": False,
                    "error": (
                        "Token liquidity below your configured minimum."
                    ),
                }

        keypair = await self.wallet_manager.get_user_keypair(user_id)
        if not keypair:
            return {"success": False, "error": "Wallet unavailable for trading"}

        slippage_bps = self._slippage_to_bps(settings.slippage_percentage)
        amount_lamports = int(amount_sol * 1e9)

        # Capture quote metadata to derive token decimals when available
        quote = None
        if execution_mode != "jito":
            quote = await self.jupiter.get_quote(
                self.SOL_MINT,
                token_mint,
                amount_lamports,
                slippage_bps=slippage_bps,
            )

        if execution_mode == "jito":
            result = await self.jupiter.execute_swap_with_jito(
                input_mint=self.SOL_MINT,
                output_mint=token_mint,
                amount=amount_lamports,
                keypair=keypair,
                slippage_bps=slippage_bps,
                tip_amount_lamports=tip_lamports or 100_000,
                priority_fee_lamports=priority_fee_lamports or 1_000_000,
            )
        else:
            result = await self.jupiter.execute_swap(
                self.SOL_MINT,
                token_mint,
                amount_lamports,
                keypair,
                slippage_bps=slippage_bps,
            )

        if not result.get("success"):
            await self._record_failed_trade(result.get("error", "Unknown error"))
            await self._persist_trade_record(
                user_id,
                token_mint,
                token_symbol,
                amount_sol,
                0.0,
                "buy",
                success=False,
                error_message=result.get("error"),
                context=context,
                metadata=metadata,
            )
            return {"success": False, "error": result.get("error", "Swap failed")}

        quote_payload = result.get("quote") if isinstance(result, dict) else None
        token_decimals = self._extract_decimals(quote_payload or quote)
        output_raw = int(
            result.get("output_amount")
            or (quote_payload or {}).get("outAmount", 0)
        )
        tokens_received = self._convert_amount(output_raw, token_decimals)
        execution_price = self._calculate_price(amount_sol, tokens_received)
        signature = result.get("signature")
        bundle_id = result.get("bundle_id") if isinstance(result, dict) else None

        position_id = signature or self._build_position_id(user_id, token_mint)

        trade_metadata = metadata or {}
        if bundle_id:
            trade_metadata = {**trade_metadata, "bundle_id": bundle_id}

        await self._persist_trade_record(
            user_id,
            token_mint,
            token_symbol,
            amount_sol,
            tokens_received,
            "buy",
            signature=signature,
            price=execution_price,
            slippage=settings.slippage_percentage,
            price_impact=result.get("price_impact"),
            position_id=position_id,
            context=context,
            metadata=trade_metadata,
        )

        await self.db.open_position(
            {
                "user_id": user_id,
                "position_id": position_id,
                "token_mint": token_mint,
                "token_symbol": token_symbol or token_mint[:6],
                "token_decimals": token_decimals,
                "entry_price": execution_price or 0.0,
                "entry_amount_sol": amount_sol,
                "entry_amount_tokens": tokens_received,
                "entry_amount_raw": output_raw,
                "entry_signature": signature,
                "entry_timestamp": datetime.utcnow(),
                "source": context,
                "metadata_json": self._serialize_metadata(trade_metadata),
                "stop_loss_percentage": (
                    settings.default_stop_loss_percentage if settings.use_stop_loss else None
                ),
                "take_profit_percentage": (
                    settings.default_take_profit_percentage
                    if settings.use_take_profit
                    else None
                ),
            }
        )

        await self._reward_user(user_id, "buy", reason)

        if self.monitor:
            self.monitor.record_trade_success()

        if self.social_marketplace and context != "copy_trade":
            try:
                await self.social_marketplace.handle_trader_execution(
                    user_id,
                    {
                        "trade_type": "buy",
                        "token_mint": token_mint,
                        "token_symbol": token_symbol,
                        "amount_sol": amount_sol,
                        "amount_tokens": tokens_received,
                        "price": execution_price,
                        "position_id": position_id,
                        "signature": signature,
                        "bundle_id": bundle_id,
                        "context": context,
                        "metadata": trade_metadata,
                    },
                )
            except Exception:
                logger.exception("Failed to propagate copy trade execution")

        logger.info(
            "BUY executed | user=%s token=%s amount_sol=%.4f tokens=%.4f signature=%s",
            user_id,
            token_mint,
            amount_sol,
            tokens_received,
            signature,
        )

        return {
            "success": True,
            "signature": signature,
            "amount_sol": amount_sol,
            "amount_tokens": tokens_received,
            "token_decimals": token_decimals,
            "price": execution_price,
            "position_id": position_id,
            "bundle_id": bundle_id,
            "metadata": trade_metadata,
        }

    async def execute_sell(
        self,
        user_id: int,
        token_mint: str,
        *,
        amount_tokens: Optional[float] = None,
        token_symbol: Optional[str] = None,
        reason: str = "manual",
        context: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Execute a token -> SOL swap for an open position."""

        position = await self.db.get_position_by_token(user_id, token_mint)
        if not position:
            return {
                "success": False,
                "error": "No open position found for that token.",
            }

        settings = await self._get_user_settings(user_id)
        slippage_bps = self._slippage_to_bps(settings.slippage_percentage)

        if amount_tokens is None:
            amount_tokens = position.entry_amount_tokens or 0.0

        if amount_tokens <= 0:
            return {"success": False, "error": "Sell amount must be positive"}

        remaining_tokens = position.entry_amount_tokens or 0.0
        if abs(amount_tokens - remaining_tokens) > 1e-6:
            return {
                "success": False,
                "error": "Partial position sells are not supported yet. Use 'all'.",
            }

        amount_raw = position.entry_amount_raw or 0
        if amount_raw <= 0:
            return {
                "success": False,
                "error": "Stored position amount is invalid, cannot sell.",
            }

        keypair = await self.wallet_manager.get_user_keypair(user_id)
        if not keypair:
            return {"success": False, "error": "Wallet unavailable for trading"}

        result = await self.jupiter.execute_swap(
            token_mint,
            self.SOL_MINT,
            amount_raw,
            keypair,
            slippage_bps=slippage_bps,
        )

        if not result.get("success"):
            await self._record_failed_trade(result.get("error", "Unknown error"))
            await self._persist_trade_record(
                user_id,
                token_mint,
                token_symbol,
                0.0,
                amount_tokens,
                "sell",
                success=False,
                error_message=result.get("error"),
                position_id=position.position_id,
                context=context,
                metadata=metadata,
            )
            return {"success": False, "error": result.get("error", "Swap failed")}

        signature = result.get("signature")
        sol_received = self._convert_amount(int(result.get("output_amount", 0)), 9)
        price = self._calculate_price(sol_received, amount_tokens)
        trade_metadata = metadata or {}

        await self._persist_trade_record(
            user_id,
            token_mint,
            token_symbol,
            sol_received,
            amount_tokens,
            "sell",
            signature=signature,
            price=price,
            slippage=settings.slippage_percentage,
            price_impact=result.get("price_impact"),
            position_id=position.position_id,
            is_position_open=False,
            context=context,
            metadata=trade_metadata,
        )

        position_updates = {
            "exit_price": price or 0.0,
            "exit_amount_sol": sol_received,
            "exit_amount_tokens": amount_tokens,
            "exit_amount_raw": amount_raw,
            "exit_signature": signature,
            "exit_timestamp": datetime.utcnow(),
        }

        serialized_metadata = self._serialize_metadata(trade_metadata)
        if serialized_metadata is not None:
            position_updates["metadata_json"] = serialized_metadata

        closed_position = await self.db.close_position(
            position.position_id,
            position_updates,
        )

        pnl = 0.0
        if closed_position and closed_position.pnl_sol is not None:
            pnl = closed_position.pnl_sol

        await self._reward_user(user_id, "sell", reason, pnl=pnl)

        if self.social_marketplace and context != "copy_trade":
            try:
                await self.social_marketplace.handle_trader_execution(
                    user_id,
                    {
                        "trade_type": "sell",
                        "token_mint": token_mint,
                        "token_symbol": token_symbol,
                        "amount_sol": sol_received,
                        "amount_tokens": amount_tokens,
                        "price": price,
                        "position_id": position.position_id,
                        "signature": signature,
                        "pnl": pnl,
                        "context": context,
                        "metadata": trade_metadata,
                    },
                )
            except Exception:
                logger.exception("Failed to propagate copy trade sell execution")

        if self.social_marketplace:
            await self.social_marketplace.update_trader_stats(
                user_id,
                {"pnl": pnl},
            )

        if self.monitor:
            self.monitor.record_trade_success()

        logger.info(
            "SELL executed | user=%s token=%s amount_tokens=%.4f sol_received=%.4f signature=%s",
            user_id,
            token_mint,
            amount_tokens,
            sol_received,
            signature,
        )

        return {
            "success": True,
            "signature": signature,
            "amount_sol": sol_received,
            "amount_tokens": amount_tokens,
            "price": price,
            "position_id": position.position_id,
            "pnl": pnl,
        }

    async def _persist_trade_record(
        self,
        user_id: int,
        token_mint: str,
        token_symbol: Optional[str],
        amount_sol: float,
        amount_tokens: float,
        trade_type: str,
        *,
        signature: Optional[str] = None,
        price: Optional[float] = None,
        slippage: Optional[float] = None,
        price_impact: Optional[float] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        position_id: Optional[str] = None,
        is_position_open: bool = True,
        context: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Persist trade record in the database."""

        trade_data = {
            "user_id": user_id,
            "signature": signature or self._build_position_id(user_id, token_mint),
            "trade_type": trade_type,
            "token_mint": token_mint,
            "token_symbol": token_symbol or token_mint[:6],
            "amount_sol": amount_sol,
            "amount_tokens": amount_tokens,
            "price": price,
            "slippage": slippage,
            "price_impact": price_impact,
            "timestamp": datetime.utcnow(),
            "success": success,
            "error_message": error_message,
            "position_id": position_id,
            "is_position_open": is_position_open,
            "context": context,
            "metadata_json": self._serialize_metadata(metadata),
        }

        await self.db.add_trade(trade_data)

    async def _reward_user(
        self,
        user_id: int,
        trade_type: str,
        reason: str,
        *,
        pnl: float = 0.0,
    ) -> None:
        if not self.rewards:
            return

        await self.rewards.award_points(
            user_id,
            REWARD_POINTS.get("successful_trade", 10),
            f"{reason}:{trade_type}",
        )

    async def _record_failed_trade(self, error: str) -> None:
        if self.monitor:
            self.monitor.record_trade_failure(error)

    async def _get_user_settings(self, user_id: int) -> SimpleNamespace:
        settings = await self.db.get_user_settings(user_id)
        if settings:
            return settings

        return SimpleNamespace(
            max_trade_size_sol=1.0,
            daily_loss_limit_sol=5.0,
            slippage_percentage=5.0,
            require_confirmation=True,
            use_stop_loss=True,
            default_stop_loss_percentage=10.0,
            use_take_profit=True,
            default_take_profit_percentage=20.0,
            check_honeypots=True,
            min_liquidity_usd=10000.0,
        )

    def _extract_decimals(self, quote: Optional[Dict]) -> int:
        if not quote:
            return 6

        if "outDecimals" in quote:
            try:
                return int(quote["outDecimals"])
            except (ValueError, TypeError):
                pass

        route_plan = quote.get("routePlan") if isinstance(quote, dict) else None
        if route_plan:
            for leg in route_plan:
                swap_info = leg.get("swapInfo", {}) if isinstance(leg, dict) else {}
                decimals = swap_info.get("outDecimals")
                if decimals is not None:
                    try:
                        return int(decimals)
                    except (ValueError, TypeError):
                        continue

        return 6

    def _convert_amount(self, amount: int, decimals: int) -> float:
        try:
            scale = 10 ** max(decimals, 0)
        except OverflowError:
            scale = 1
        return amount / scale if scale else float(amount)

    def _calculate_price(self, sol_amount: float, token_amount: float) -> Optional[float]:
        if token_amount and token_amount > 0:
            return sol_amount / token_amount
        return None

    def _slippage_to_bps(self, slippage_percentage: Optional[float]) -> int:
        if slippage_percentage is None:
            return 50
        return max(1, int(slippage_percentage * 100))

    def _build_position_id(self, user_id: int, token_mint: str) -> str:
        return f"{user_id}-{token_mint}-{datetime.utcnow().timestamp()}"

    def _serialize_metadata(self, metadata: Optional[Dict[str, Any]]) -> Optional[str]:
        if not metadata:
            return None

        try:
            return json.dumps(metadata)
        except (TypeError, ValueError):
            logger.debug("Failed to serialize trade metadata", exc_info=True)
            return None

