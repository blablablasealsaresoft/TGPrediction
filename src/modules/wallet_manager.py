"""
USER WALLET MANAGEMENT
Each user gets their own dedicated trading wallet
Secure encryption of private keys
"""

import os
import base58
import logging
from typing import Optional, Dict
from datetime import datetime
from cryptography.fernet import Fernet
from solders.keypair import Keypair
from solana.rpc.async_api import AsyncClient
from sqlalchemy import select

from src.modules.database import UserWallet, DatabaseManager

logger = logging.getLogger(__name__)


class WalletEncryption:
    """Handles encryption/decryption of wallet private keys"""
    
    def __init__(self):
        # Get or generate master encryption key
        self.master_key = self._get_or_create_master_key()
        self.fernet = Fernet(self.master_key)
    
    def _get_or_create_master_key(self) -> bytes:
        """Get master key from env or generate new one"""
        key_str = os.getenv('WALLET_ENCRYPTION_KEY')
        
        if key_str:
            return key_str.encode()
        
        # Generate new key
        new_key = Fernet.generate_key()
        logger.warning("Generated new wallet encryption key. Add to .env:")
        logger.warning(f"WALLET_ENCRYPTION_KEY={new_key.decode()}")
        return new_key
    
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
        wallet = await self._get_wallet_from_db(user_id)
        
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
    
    def clear_cache(self):
        """Clear wallet cache (security)"""
        self._wallet_cache = {}
        logger.info("Wallet cache cleared")

