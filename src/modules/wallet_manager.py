"""
USER WALLET MANAGEMENT
Each user gets their own dedicated trading wallet
Secure encryption of private keys
"""

import os
import base58
import logging
from typing import Optional, Dict, Union
from datetime import datetime
from cryptography.fernet import Fernet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from sqlalchemy import select

from src.modules.database import UserWallet, DatabaseManager

logger = logging.getLogger(__name__)


class WalletEncryption:
    """Handles encryption/decryption of wallet private keys"""
    
    def __init__(self, master_key: Optional[Union[str, bytes]] = None):
        """Initialize wallet encryption helper.

        Args:
            master_key: Optional override for the Fernet key. When not provided
                the value is read from ``WALLET_ENCRYPTION_KEY``. The key must
                be a url-safe base64 encoded 32-byte string as required by
                :class:`cryptography.fernet.Fernet`.
        """

        self.master_key = self._load_master_key(master_key)
        self.fernet = Fernet(self.master_key)

    @staticmethod
    def generate_key() -> str:
        """Generate a new wallet encryption key."""

        return Fernet.generate_key().decode()

    @staticmethod
    def validate_key(key: Union[str, bytes]) -> bytes:
        """Validate that the provided key is a proper Fernet key."""

        if not key:
            raise ValueError("Wallet encryption key cannot be empty")

        key_bytes = key if isinstance(key, bytes) else key.encode()

        try:
            # Instantiating Fernet validates the key structure
            Fernet(key_bytes)
        except Exception as exc:  # pragma: no cover - cryptography raises ValueError
            raise ValueError(
                "Invalid WALLET_ENCRYPTION_KEY provided. The key must be a "
                "urlsafe base64-encoded 32-byte string. Generate one with "
                "WalletEncryption.generate_key() or the rotate_wallet_key.py "
                "utility."
            ) from exc

        return key_bytes

    def _load_master_key(self, master_key: Optional[Union[str, bytes]]) -> bytes:
        """Load the master key from an override or the environment."""

        if master_key is not None:
            return self.validate_key(master_key)

        key_str = os.getenv('WALLET_ENCRYPTION_KEY')
        if not key_str:
            raise RuntimeError(
                "WALLET_ENCRYPTION_KEY environment variable is required. "
                "Set it to a Fernet key before starting the bot. Use the "
                "scripts/rotate_wallet_key.py tool to generate or rotate "
                "keys and store them securely (for example in a secrets "
                "manager or HSM)."
            )

        return self.validate_key(key_str)
    
    def encrypt_private_key(self, private_key_bytes: bytes) -> str:
        """Encrypt private key"""
        return self.fernet.encrypt(private_key_bytes).decode()
    
    def decrypt_private_key(self, encrypted_key: str) -> bytes:
        """Decrypt private key"""
        return self.fernet.decrypt(encrypted_key.encode())


class UserWalletManager:
    """
    Manages individual user wallets
    Each user gets their own Solana wallet for trading
    """
    
    def __init__(self, db: DatabaseManager, rpc_client: AsyncClient):
        self.db = db
        self.client = rpc_client
        self.encryption = WalletEncryption()
        self._wallet_cache = {}  # Cache keypairs in memory
    
    async def get_or_create_user_wallet(
        self,
        user_id: int,
        username: str = None
    ) -> Dict:
        """
        Get existing wallet or create new one for user
        
        Returns:
            Dict with public_key, sol_balance, is_new
        """
        # Check if user already has wallet
        logger.info(f"🔍 Looking for existing wallet for user {user_id}...")
        wallet = await self._get_wallet_from_db(user_id)
        
        if wallet:
            logger.info(f"✅ Found existing wallet: {wallet.public_key}")
        
        if wallet:
            # Update balance
            balance = await self._get_sol_balance(wallet.public_key)
            
            async with self.db.async_session() as session:
                wallet.sol_balance = balance
                wallet.last_balance_update = datetime.utcnow()
                wallet.last_used = datetime.utcnow()
                await session.commit()
            
            return {
                'public_key': wallet.public_key,
                'sol_balance': balance,
                'is_new': False,
                'created_at': wallet.created_at
            }
        
        # Create new wallet for user
        logger.warning(f"⚠️ No existing wallet found for user {user_id}")
        logger.info(f"Creating new wallet for user {user_id}")
        
        # Generate new Solana keypair
        keypair = Keypair()
        public_key = str(keypair.pubkey())
        private_key_bytes = bytes(keypair)
        
        # Encrypt private key
        encrypted_key = self.encryption.encrypt_private_key(private_key_bytes)
        
        # Save to database
        async with self.db.async_session() as session:
            user_wallet = UserWallet(
                user_id=user_id,
                telegram_username=username,
                public_key=public_key,
                encrypted_private_key=encrypted_key,
                sol_balance=0.0,
                last_balance_update=datetime.utcnow()
            )
            session.add(user_wallet)
            await session.commit()
        
        # Cache the keypair
        self._wallet_cache[user_id] = keypair
        
        logger.info(f"✅ Created wallet for user {user_id}: {public_key}")
        
        return {
            'public_key': public_key,
            'sol_balance': 0.0,
            'is_new': True,
            'created_at': datetime.utcnow()
        }
    
    async def get_user_keypair(self, user_id: int) -> Optional[Keypair]:
        """
        Get user's keypair for signing transactions
        Decrypts from database and caches in memory
        """
        # Check cache first
        if user_id in self._wallet_cache:
            return self._wallet_cache[user_id]
        
        # Get from database
        wallet = await self._get_wallet_from_db(user_id)
        if not wallet:
            return None
        
        # Decrypt private key
        try:
            private_key_bytes = self.encryption.decrypt_private_key(
                wallet.encrypted_private_key
            )
            keypair = Keypair.from_bytes(private_key_bytes)
            
            # Cache it
            self._wallet_cache[user_id] = keypair
            
            # Update last used
            async with self.db.async_session() as session:
                wallet.last_used = datetime.utcnow()
                await session.commit()
            
            return keypair
            
        except Exception as e:
            logger.error(f"Failed to decrypt wallet for user {user_id}: {e}")
            return None
    
    async def get_user_balance(self, user_id: int) -> float:
        """Get user's SOL balance"""
        wallet = await self._get_wallet_from_db(user_id)
        if not wallet:
            return 0.0
        
        # Get fresh balance from RPC
        balance = await self._get_sol_balance(wallet.public_key)
        
        # Update cached balance
        async with self.db.async_session() as session:
            wallet.sol_balance = balance
            wallet.last_balance_update = datetime.utcnow()
            await session.commit()
        
        return balance
    
    async def get_user_wallet_address(self, user_id: int) -> Optional[str]:
        """Get user's wallet public address"""
        wallet = await self._get_wallet_from_db(user_id)
        return wallet.public_key if wallet else None
    
    async def _get_wallet_from_db(self, user_id: int) -> Optional[UserWallet]:
        """Get wallet record from database"""
        async with self.db.async_session() as session:
            result = await session.execute(
                select(UserWallet).where(UserWallet.user_id == user_id)
            )
            return result.scalar_one_or_none()
    
    async def _get_sol_balance(self, public_key: str) -> float:
        """Get SOL balance from RPC"""
        try:
            from solders.pubkey import Pubkey
            pubkey = Pubkey.from_string(public_key)
            response = await self.client.get_balance(pubkey)
            
            if response.value is not None:
                # Convert lamports to SOL
                return response.value / 1e9
            return 0.0
            
        except Exception as e:
            logger.error(f"Error getting balance for {public_key}: {e}")
            return 0.0
    
    async def get_all_user_wallets(self, limit: int = 100) -> list:
        """Get list of all user wallets (admin function)"""
        async with self.db.async_session() as session:
            result = await session.execute(
                select(UserWallet)
                .order_by(UserWallet.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def export_private_key(self, user_id: int) -> Optional[str]:
        """
        Export user's private key in base58 format (for importing to Phantom, etc.)
        
        Returns:
            Base58-encoded private key string, or None if wallet not found
        """
        keypair = await self.get_user_keypair(user_id)
        if not keypair:
            return None
        
        # Export as base58 (compatible with Phantom, Solflare, etc.)
        private_key_bytes = bytes(keypair)
        private_key_b58 = base58.b58encode(private_key_bytes).decode()
        
        logger.info(f"User {user_id} exported their private key")
        return private_key_b58
    
    def clear_cache(self):
        """Clear wallet cache (security)"""
        self._wallet_cache = {}
        logger.info("Wallet cache cleared")

