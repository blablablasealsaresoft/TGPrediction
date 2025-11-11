#!/usr/bin/env python3
"""
Migrate user_id columns from INTEGER to BIGINT in PostgreSQL.

Telegram user IDs can exceed INT32 range (2^31-1 = 2,147,483,647).
This script safely migrates all user_id columns to BIGINT.

Usage:
    python scripts/migrate_user_id_to_bigint.py
"""

import asyncio
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
import asyncpg

load_dotenv()

# Tables with user_id columns
TABLES_TO_MIGRATE = [
    'trades',
    'user_wallets',
    'tracked_wallets',
    'positions',
    'user_settings',
    'snipe_runs',
]

async def migrate_to_bigint():
    """Migrate all user_id columns to BIGINT"""
    
    # Get database connection
    db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://trader:T_TleomdfYmv-13lnjehNu7xp-q99RRXyW13XreWof8@localhost:5432/trading_bot')
    
    # Parse connection string
    if db_url.startswith('postgresql+asyncpg://'):
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    print(f"🔄 Connecting to database...")
    
    try:
        conn = await asyncpg.connect(db_url)
        
        print(f"✅ Connected successfully\n")
        
        # Check current column types
        print("📊 Current column types:")
        for table in TABLES_TO_MIGRATE:
            result = await conn.fetchrow("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = $1 AND column_name = 'user_id'
            """, table)
            
            if result:
                print(f"   {table}.user_id: {result['data_type']}")
            else:
                print(f"   {table}: table or column not found")
        
        print("\n🔧 Starting migration...\n")
        
        # Migrate each table
        for table in TABLES_TO_MIGRATE:
            try:
                # Check if column exists
                result = await conn.fetchrow("""
                    SELECT data_type 
                    FROM information_schema.columns 
                    WHERE table_name = $1 AND column_name = 'user_id'
                """, table)
                
                if not result:
                    print(f"⚠️  Skipping {table}: no user_id column")
                    continue
                
                if result['data_type'] == 'bigint':
                    print(f"✅ {table}: already BIGINT")
                    continue
                
                print(f"🔄 Migrating {table}.user_id to BIGINT...")
                
                # Alter column type
                await conn.execute(f"""
                    ALTER TABLE {table} 
                    ALTER COLUMN user_id TYPE BIGINT
                """)
                
                print(f"✅ {table}: migrated successfully")
                
            except Exception as e:
                print(f"❌ {table}: migration failed - {e}")
                continue
        
        # Also migrate copy_trader_id in tracked_wallets
        print(f"\n🔄 Migrating tracked_wallets.copy_trader_id to BIGINT...")
        try:
            await conn.execute("""
                ALTER TABLE tracked_wallets 
                ALTER COLUMN copy_trader_id TYPE BIGINT
            """)
            print(f"✅ tracked_wallets.copy_trader_id: migrated successfully")
        except Exception as e:
            print(f"❌ tracked_wallets.copy_trader_id: {e}")
        
        # Verify migration
        print("\n📊 Final column types:")
        for table in TABLES_TO_MIGRATE:
            result = await conn.fetchrow("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = $1 AND column_name = 'user_id'
            """, table)
            
            if result:
                print(f"   {table}.user_id: {result['data_type']}")
        
        result = await conn.fetchrow("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'tracked_wallets' AND column_name = 'copy_trader_id'
        """)
        if result:
            print(f"   tracked_wallets.copy_trader_id: {result['data_type']}")
        
        await conn.close()
        
        print("\n✅ Migration completed successfully!")
        print("🎯 You can now use Telegram user IDs up to 9,223,372,036,854,775,807")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*60)
    print("🔧 PostgreSQL user_id Migration: INTEGER → BIGINT")
    print("="*60 + "\n")
    
    asyncio.run(migrate_to_bigint())

