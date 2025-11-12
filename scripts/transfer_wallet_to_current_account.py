"""
Transfer wallet from old Telegram account to current one
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.modules.database import DatabaseManager, UserWallet
from sqlalchemy import select, delete
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def transfer_wallet():
    """Transfer wallet from old account (C K) to new account (CKFidel)"""
    
    old_user_id = 1928855074  # C K
    new_user_id = 8059844643  # CKFidel (current account)
    
    database_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://trader:T_TleomdfYmv-13lnjehNu7xp-q99RRXyW13XreWof8@postgres:5432/trading_bot')
    
    logger.info("=" * 60)
    logger.info("🔄 TRANSFERRING WALLET BETWEEN ACCOUNTS")
    logger.info("=" * 60)
    logger.info(f"FROM: User {old_user_id} (C K)")
    logger.info(f"TO:   User {new_user_id} (CKFidel)")
    
    try:
        db = DatabaseManager(database_url)
        await db.init_db()
        
        async with db.async_session() as session:
            # Get old wallet
            result = await session.execute(
                select(UserWallet).where(UserWallet.user_id == old_user_id)
            )
            old_wallet = result.scalar_one_or_none()
            
            if not old_wallet:
                logger.error(f"❌ Wallet for user {old_user_id} not found!")
                return
            
            logger.info(f"✅ Found old wallet:")
            logger.info(f"   Address: {old_wallet.public_key}")
            logger.info(f"   Balance: {old_wallet.sol_balance} SOL")
            
            # Delete new empty wallet if it exists
            await session.execute(
                delete(UserWallet).where(UserWallet.user_id == new_user_id)
            )
            logger.info(f"🗑️ Deleted new empty wallet for user {new_user_id}")
            
            # Update user_id to transfer wallet
            old_wallet.user_id = new_user_id
            old_wallet.telegram_username = "CKFidel"
            
            await session.commit()
            logger.info("=" * 60)
            logger.info("✅ WALLET TRANSFERRED SUCCESSFULLY!")
            logger.info("=" * 60)
            logger.info(f"🔐 Address: {old_wallet.public_key}")
            logger.info(f"💰 Balance: {old_wallet.sol_balance} SOL")
            logger.info(f"👤 Now belongs to user {new_user_id} (CKFidel)")
            logger.info("=" * 60)
            logger.info("📱 Send /start in Telegram NOW - you'll see your OLD wallet!")
            logger.info("=" * 60)
        
        await db.engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ Error transferring wallet: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(transfer_wallet())

