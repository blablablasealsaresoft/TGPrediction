#!/usr/bin/env python3
"""
Fix for Telegram CallbackQuery AttributeError
This script fixes the bug where button callbacks pass the wrong object type
"""

import sys
from pathlib import Path

def fix_main_py():
    """Fix the callback bugs in main.py"""
    
    main_py_path = Path("main.py")
    
    if not main_py_path.exists():
        print("❌ Error: main.py not found!")
        print("   Make sure you're running this script from the project root directory")
        return False
    
    print("📖 Reading main.py...")
    with open(main_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup original file
    backup_path = main_py_path.with_suffix('.py.backup')
    print(f"💾 Creating backup: {backup_path}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Fix #1: my_stats button callback
    original_1 = 'elif data == "my_stats":\n            await self.my_stats_command(query, context)'
    fixed_1 = 'elif data == "my_stats":\n            await self.my_stats_command(update, context)'
    
    # Fix #2: leaderboard button callback
    original_2 = 'elif data == "leaderboard":\n            await self.leaderboard_command(query, context)'
    fixed_2 = 'elif data == "leaderboard":\n            await self.leaderboard_command(update, context)'
    
    fixes_applied = 0
    
    if original_1 in content:
        print("🔧 Fixing my_stats callback...")
        content = content.replace(original_1, fixed_1)
        fixes_applied += 1
    else:
        print("⚠️  my_stats callback not found or already fixed")
    
    if original_2 in content:
        print("🔧 Fixing leaderboard callback...")
        content = content.replace(original_2, fixed_2)
        fixes_applied += 1
    else:
        print("⚠️  leaderboard callback not found or already fixed")
    
    if fixes_applied > 0:
        print(f"💾 Writing fixed version to main.py...")
        with open(main_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Applied {fixes_applied} fix(es) successfully!")
        print(f"✅ Backup saved to: {backup_path}")
        return True
    else:
        print("ℹ️  No fixes needed - file appears to already be fixed!")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Revolutionary Trading Bot - Callback Bug Fix")
    print("=" * 60)
    print()
    
    success = fix_main_py()
    
    print()
    if success:
        print("✅ Fix applied successfully!")
        print()
        print("📋 Next steps:")
        print("   1. Restart your bot")
        print("   2. Test the '📊 My Stats' button")
        print("   3. Test the '🏆 Leaderboard' button")
        print()
        print("🔥 Your bot is ready to dominate!")
    else:
        print("❌ Fix failed - please apply manually")
        print()
        print("Manual fix instructions:")
        print("   1. Open main.py")
        print("   2. Find line ~2259: await self.my_stats_command(query, context)")
        print("   3. Change 'query' to 'update'")
        print("   4. Find line ~2262: await self.leaderboard_command(query, context)")
        print("   5. Change 'query' to 'update'")
    
    print("=" * 60)
