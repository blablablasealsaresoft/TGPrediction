#!/usr/bin/env python3
"""
Project setup script
Creates necessary directories, copies config files, etc.
"""

import os
import sys
import shutil
from pathlib import Path


def setup_directories():
    """Create necessary directories"""
    dirs = [
        'logs',
        'data',
        'backups',
        'config'
    ]
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")


def setup_config():
    """Setup configuration files"""
    # Copy .env.example to .env if .env doesn't exist
    env_example = Path('config/.env.example')
    env_file = Path('.env')
    
    if env_example.exists() and not env_file.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from .env.example")
        print("⚠️  IMPORTANT: Edit .env with your actual credentials!")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("⚠️  Warning: .env.example not found")


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("✓ Dependencies installed")


def main():
    """Main setup function"""
    print("=" * 60)
    print("SOLANA TRADING BOT - PROJECT SETUP")
    print("=" * 60)
    print()
    
    check_python_version()
    setup_directories()
    setup_config()
    
    # Ask if user wants to install dependencies
    response = input("\nInstall Python dependencies? (y/n): ")
    if response.lower() == 'y':
        install_dependencies()
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit .env file with your credentials")
    print("2. Run: python scripts/run_bot.py")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()

