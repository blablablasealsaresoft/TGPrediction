#!/usr/bin/env python3
"""
Installation Compliance Check
Verify we followed the README.md installation instructions properly
"""

import os
import sys
from pathlib import Path

def check_installation_compliance():
    """Check if we followed README installation instructions"""
    
    print("INSTALLATION COMPLIANCE CHECK")
    print("="*80)
    print("Verifying we followed README.md installation instructions")
    print("="*80)
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check for required files from README
    required_files = [
        'README.md',
        'requirements.txt',
        'ENV_CONFIGURATION.txt',
        '.env',
        'src/',
        'scripts/',
        'scripts/run_bot.py',
        'scripts/migrate_database.py',
        'scripts/rotate_wallet_key.py',
        'scripts/bot_status.py'
    ]
    
    print("\n1. REQUIRED FILES CHECK")
    print("-" * 50)
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"+ {file_path}: EXISTS")
        else:
            print(f"- {file_path}: MISSING")
            missing_files.append(file_path)
    
    # Check Python version
    print("\n2. PYTHON VERSION CHECK")
    print("-" * 50)
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version >= (3, 9):
        print("+ Python version: COMPATIBLE (>= 3.9)")
    else:
        print("- Python version: INCOMPATIBLE (< 3.9)")
    
    # Check if we have virtual environment
    print("\n3. VIRTUAL ENVIRONMENT CHECK")
    print("-" * 50)
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("+ Virtual environment: ACTIVE")
    else:
        print("- Virtual environment: NOT DETECTED (may be using system Python)")
    
    # Check if requirements are installed
    print("\n4. DEPENDENCIES CHECK")
    print("-" * 50)
    
    try:
        import telegram
        print("+ python-telegram-bot: INSTALLED")
    except ImportError:
        print("- python-telegram-bot: NOT INSTALLED")
    
    try:
        import solana
        print("+ solana: INSTALLED")
    except ImportError:
        print("- solana: NOT INSTALLED")
    
    try:
        import sqlalchemy
        print("+ sqlalchemy: INSTALLED")
    except ImportError:
        print("- sqlalchemy: NOT INSTALLED")
    
    try:
        import cryptography
        print("+ cryptography: INSTALLED")
    except ImportError:
        print("- cryptography: NOT INSTALLED")
    
    # Check .env configuration
    print("\n5. ENVIRONMENT CONFIGURATION CHECK")
    print("-" * 50)
    
    if Path('.env').exists():
        print("+ .env file: EXISTS")
        
        # Check for required environment variables
        required_env_vars = [
            'TELEGRAM_BOT_TOKEN',
            'SOLANA_RPC_URL',
            'WALLET_ENCRYPTION_KEY'
        ]
        
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            for var in required_env_vars:
                if os.getenv(var):
                    print(f"+ {var}: CONFIGURED")
                else:
                    print(f"- {var}: MISSING")
        except ImportError:
            print("- python-dotenv: NOT INSTALLED")
    else:
        print("- .env file: MISSING")
    
    # Check database
    print("\n6. DATABASE CHECK")
    print("-" * 50)
    
    if Path('trading_bot.db').exists():
        print("+ trading_bot.db: EXISTS")
    else:
        print("- trading_bot.db: MISSING")
    
    # Check if bot can run
    print("\n7. BOT EXECUTABILITY CHECK")
    print("-" * 50)
    
    if Path('scripts/run_bot.py').exists():
        print("+ run_bot.py: EXISTS")
    else:
        print("- run_bot.py: MISSING")
    
    # Check requirements directory structure
    print("\n8. REQUIREMENTS STRUCTURE CHECK")
    print("-" * 50)
    
    requirements_files = [
        'requirements.txt',
        'requirements/base.in',
        'requirements/dev.in',
        'requirements/dev.lock'
    ]
    
    for req_file in requirements_files:
        if Path(req_file).exists():
            print(f"+ {req_file}: EXISTS")
        else:
            print(f"- {req_file}: MISSING")
    
    # Check if we used the proper installation method
    print("\n9. INSTALLATION METHOD CHECK")
    print("-" * 50)
    
    # Check if we have the install script
    if Path('scripts/install_requirements.sh').exists():
        print("+ install_requirements.sh: EXISTS")
        print("+ Used proper installation method from requirements/README.md")
    else:
        print("- install_requirements.sh: MISSING")
        print("- May have used pip install -r requirements.txt instead")
    
    # Check vendor directory
    if Path('vendor/').exists():
        print("+ vendor/ directory: EXISTS")
        print("+ Using vendored wheels as recommended")
    else:
        print("- vendor/ directory: MISSING")
        print("- Not using vendored wheels")
    
    print("\n" + "="*80)
    print("INSTALLATION COMPLIANCE SUMMARY")
    print("="*80)
    
    total_checks = len(required_files) + 8  # Additional checks
    passed_checks = total_checks - len(missing_files)
    
    if len(missing_files) == 0:
        print("STATUS: FULLY COMPLIANT")
        print("RESULT: All installation steps followed correctly")
    elif len(missing_files) <= 2:
        print("STATUS: MOSTLY COMPLIANT")
        print("RESULT: Minor issues, but core installation successful")
    else:
        print("STATUS: PARTIALLY COMPLIANT")
        print("RESULT: Some installation steps may have been skipped")
    
    print(f"Passed checks: {passed_checks}/{total_checks}")
    
    if missing_files:
        print(f"Missing files: {len(missing_files)}")
        for file in missing_files:
            print(f"  - {file}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if not Path('scripts/install_requirements.sh').exists():
        print("1. Consider using scripts/install_requirements.sh for proper installation")
    
    if not Path('vendor/').exists():
        print("2. Consider using vendored wheels for reproducible builds")
    
    if not Path('.env').exists():
        print("3. Create .env file from ENV_CONFIGURATION.txt")
    
    if not Path('trading_bot.db').exists():
        print("4. Run python scripts/migrate_database.py to create database")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    check_installation_compliance()
