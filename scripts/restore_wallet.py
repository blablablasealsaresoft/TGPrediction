"""
Emergency Wallet Restoration Script
Restores user wallet with specific private key to database
"""
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.database import DatabaseManager, UserWallet
from cryptography.fernet import Fernet
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def restore_wallet():
    """Restore user wallet with their original private key"""
    
    # Configuration
    user_id = 1928855074  # C K's Telegram ID from the /start message
    telegram_username = "C K"
    
    # OLD WALLET (with 0.6064 SOL)
    old_public_key = "DbjdbXRrfoqGmUYb4MXLTQ9H1bhqFKiP3g2sPanhucNx"
    wallet_private_key = os.getenv('WALLET_PRIVATE_KEY', '2KBD49gknMGpsVSJWuUFbTPLsVLd4kMEN8n8cBERvJFML8sBzavGqpHH14mYUwDWYHZ6EdTx1DzHxto6PUsUVpke')
    encryption_key = os.getenv('WALLET_ENCRYPTION_KEY', 'AVJgGXLjc2lnAHWv-SSdAVppvmXCst89sJPPhEIVGX4=')
    
    # Database connection
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://trader:T_TleomdfYmv-13lnjehNu7xp-q99RRXyW13XreWof8@postgres:5432/trading_bot')
    
    logger.info(f"🔧 Restoring wallet for user {user_id} ({telegram_username})")
    logger.info(f"📍 Old wallet address: {old_public_key}")
    logger.info(f"💰 Expected balance: 0.6064 SOL")
    
    try:
        # Initialize database
        db = DatabaseManager(database_url)
        await db.init_db()
        logger.info("✅ Database initialized")
        
        # Encrypt the private key
        cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        encrypted_private_key = cipher.encrypt(wallet_private_key.encode()).decode()
        
        # Check if wallet already exists
        async with db.async_session() as session:
            from sqlalchemy import select
            result = await session.execute(
                select(UserWallet).where(UserWallet.user_id == user_id)
            )
            existing_wallet = result.scalar_one_or_none()
            
            if existing_wallet:
                logger.info(f"📝 Updating existing wallet record...")
                existing_wallet.public_key = old_public_key
                existing_wallet.encrypted_private_key = encrypted_private_key
                existing_wallet.telegram_username = telegram_username
            else:
                logger.info(f"🆕 Creating new wallet record...")
                new_wallet = UserWallet(
                    user_id=user_id,
                    telegram_username=telegram_username,
                    public_key=old_public_key,
                    encrypted_private_key=encrypted_private_key,
                    sol_balance=0.6064  # Last known balance
                )
                new_wallet.is_active = True
                session.add(new_wallet)
            
            await session.commit()
            logger.info("✅ Wallet restored successfully!")
            logger.info(f"🔐 Address: {old_public_key}")
            logger.info(f"💰 Your funds are safe on the blockchain!")
            logger.info(f"📱 Try /start in Telegram - you should see your old wallet")
        
        await db.engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ Error restoring wallet: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(restore_wallet())
