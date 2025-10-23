import pytest
from unittest.mock import AsyncMock

from solders.keypair import Keypair

from src.modules.trade_execution import TradeExecutionService
from src.modules.social_trading import RewardSystem


class StubWalletManager:
    def __init__(self):
        self.keypair = Keypair()
        self.balance = 10.0

    async def get_user_keypair(self, user_id):
        return self.keypair

    async def get_user_balance(self, user_id):
        return self.balance

    async def get_user_wallet_address(self, user_id):
        return str(self.keypair.pubkey())


class StubProtection:
    async def comprehensive_token_check(self, token_mint: str):
        return {"is_safe": True, "details": {"liquidity_usd": 20000}}


class StubMonitor:
    def __init__(self):
        self.success = 0
        self.failure = 0

    def record_trade_success(self):
        self.success += 1

    def record_trade_failure(self, error: str):
        self.failure += 1


class StubMarketplace:
    def __init__(self):
        self.update_trader_stats = AsyncMock()
        self.handle_trader_execution = AsyncMock(return_value=[])


@pytest.mark.asyncio
async def test_execute_buy_success(mock_database):
    wallet_manager = StubWalletManager()

    jupiter = AsyncMock()
    jupiter.get_quote.return_value = {"outAmount": 500000000, "outDecimals": 6}
    jupiter.execute_swap.return_value = {
        "success": True,
        "signature": "sig-buy",
        "output_amount": 500000000,
        "price_impact": 0.2,
    }

    service = TradeExecutionService(
        mock_database,
        wallet_manager,
        jupiter,
        protection=StubProtection(),
        monitor=StubMonitor(),
        social_marketplace=StubMarketplace(),
        rewards=RewardSystem(),
    )

    result = await service.execute_buy(1, "TokenMint", 0.5, token_symbol="TEST")

    assert result["success"] is True
    assert result["signature"] == "sig-buy"
    assert pytest.approx(result["amount_sol"], rel=1e-6) == 0.5

    trades = await mock_database.get_user_trades(user_id=1)
    assert len(trades) == 1
    assert trades[0].trade_type == "buy"

    positions = await mock_database.get_open_positions(user_id=1)
    assert len(positions) == 1
    assert positions[0].token_mint == "TokenMint"
    assert positions[0].entry_amount_raw == 500000000


@pytest.mark.asyncio
async def test_execute_sell_success(mock_database):
    wallet_manager = StubWalletManager()

    buy_result = {
        "success": True,
        "signature": "sig-buy",
        "output_amount": 400000000,
        "price_impact": 0.1,
    }
    sell_result = {
        "success": True,
        "signature": "sig-sell",
        "output_amount": 450000000,
        "price_impact": 0.05,
    }

    jupiter = AsyncMock()
    jupiter.get_quote.return_value = {"outAmount": 400000000, "outDecimals": 6}
    jupiter.execute_swap = AsyncMock(side_effect=[buy_result, sell_result])

    marketplace = StubMarketplace()
    monitor = StubMonitor()

    service = TradeExecutionService(
        mock_database,
        wallet_manager,
        jupiter,
        protection=StubProtection(),
        monitor=monitor,
        social_marketplace=marketplace,
        rewards=RewardSystem(),
    )

    await service.execute_buy(1, "TokenMint", 0.4, token_symbol="TEST")
    result = await service.execute_sell(1, "TokenMint")

    assert result["success"] is True
    assert result["signature"] == "sig-sell"
    assert pytest.approx(result["amount_sol"], rel=1e-6) == 0.45
    assert marketplace.update_trader_stats.await_count == 1
    assert monitor.success >= 2

    trades = await mock_database.get_user_trades(user_id=1)
    assert len(trades) == 2
    assert trades[-1].trade_type == "sell"
    assert trades[-1].is_position_open is False

    positions = await mock_database.get_open_positions(user_id=1)
    assert positions == []


@pytest.mark.asyncio
async def test_sell_without_position(mock_database):
    wallet_manager = StubWalletManager()
    jupiter = AsyncMock()
    jupiter.get_quote.return_value = {"outAmount": 400000000, "outDecimals": 6}
    jupiter.execute_swap.return_value = {
        "success": True,
        "signature": "sig",
        "output_amount": 400000000,
    }

    service = TradeExecutionService(
        mock_database,
        wallet_manager,
        jupiter,
        protection=StubProtection(),
        monitor=StubMonitor(),
        social_marketplace=StubMarketplace(),
        rewards=RewardSystem(),
    )

    result = await service.execute_sell(1, "TokenMint")
    assert result["success"] is False
    assert "No open position" in result["error"]
