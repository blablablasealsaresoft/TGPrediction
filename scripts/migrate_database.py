#!/usr/bin/env python3
"""
Database Migration Script
Adds new columns to existing database without losing data
"""

import sqlite3
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def migrate_database():
    """Add sniper columns to user_settings table"""
    
    db_path = 'trading_bot.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Run the bot first to create the database.")
        return False
    
    print("🔧 Migrating database...")
    print(f"Database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user_settings table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_settings'")
        if not cursor.fetchone():
            print("Creating user_settings table...")
            cursor.execute("""
                CREATE TABLE user_settings (
                    user_id INTEGER PRIMARY KEY,
                    auto_trading_enabled BOOLEAN DEFAULT 0,
                    max_trade_size_sol REAL DEFAULT 1.0,
                    daily_loss_limit_sol REAL DEFAULT 5.0,
                    slippage_percentage REAL DEFAULT 5.0,
                    require_confirmation BOOLEAN DEFAULT 1,
                    use_stop_loss BOOLEAN DEFAULT 1,
                    default_stop_loss_percentage REAL DEFAULT 10.0,
                    use_take_profit BOOLEAN DEFAULT 1,
                    default_take_profit_percentage REAL DEFAULT 20.0,
                    check_honeypots BOOLEAN DEFAULT 1,
                    min_liquidity_usd REAL DEFAULT 10000.0,
                    snipe_enabled BOOLEAN DEFAULT 0,
                    snipe_max_amount REAL DEFAULT 0.1,
                    snipe_min_liquidity REAL DEFAULT 10000.0,
                    snipe_min_confidence REAL DEFAULT 0.65,
                    snipe_max_daily INTEGER DEFAULT 10,
                    snipe_only_strong_buy BOOLEAN DEFAULT 1,
                    snipe_daily_used INTEGER DEFAULT 0,
                    snipe_last_reset DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Created user_settings table")
        else:
            # Table exists, add missing columns
            print("Checking for missing columns...")
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(user_settings)")
            existing_columns = {row[1] for row in cursor.fetchall()}
            
            # Define new columns to add
            new_columns = {
                'snipe_enabled': 'BOOLEAN DEFAULT 0',
                'snipe_max_amount': 'REAL DEFAULT 0.1',
                'snipe_min_liquidity': 'REAL DEFAULT 10000.0',
                'snipe_min_confidence': 'REAL DEFAULT 0.65',
                'snipe_max_daily': 'INTEGER DEFAULT 10',
                'snipe_only_strong_buy': 'BOOLEAN DEFAULT 1',
                'snipe_daily_used': 'INTEGER DEFAULT 0',
                'snipe_last_reset': 'DATETIME'
            }
            
            # Add missing columns
            added = 0
            for col_name, col_type in new_columns.items():
                if col_name not in existing_columns:
                    print(f"  Adding column: {col_name}")
                    cursor.execute(f"ALTER TABLE user_settings ADD COLUMN {col_name} {col_type}")
                    added += 1
            
            if added > 0:
                print(f"✅ Added {added} new columns")
            else:
                print("✅ All columns already exist")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database migration complete!")
        print("Restart your bot now.")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION")
    print("=" * 60)
    print("Adding auto-sniper columns to database\n")
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration successful!")
        print("You can now use the auto-sniper features.")
        sys.exit(0)
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)

