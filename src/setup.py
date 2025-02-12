#!/usr/bin/env python3
"""
Automated setup and configuration script for The Everything Bot.
Makes bot setup as simple as possible for new users.
"""

import os
import sys
import secrets
import subprocess
import platform
from pathlib import Path

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_python_version():
    """Ensure Python 3.8+ is installed."""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)

def install_dependencies():
    """Install required Python packages."""
    print("🔄 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies.")
        sys.exit(1)

def generate_env_file():
    """Interactive .env file generation."""
    clear_screen()
    print("🤖 The Everything Bot - Setup Wizard 🤖")
    print("----------------------------------------")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("⚠️ .env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            return

    # Discord Bot Token
    while True:
        token = input("1. Enter your Discord Bot Token: ").strip()
        if token and len(token) > 50:  # Basic token validation
            break
        print("❌ Invalid token. Please try again.")

    # Generate encryption key
    encryption_key = secrets.token_hex(32)

    # Create .env file
    env_content = f"""# The Everything Bot Configuration
DISCORD_TOKEN={token}
ENCRYPTION_KEY={encryption_key}
BOT_PREFIX=/
BOT_ACTIVITY=Helping servers!
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
LEVELING_ENABLED=true
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ .env file created successfully!")

def create_virtual_env():
    """Create a virtual environment if not exists."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("🔧 Creating virtual environment...")
        
        # Determine the correct venv creation command
        if platform.system() == "Windows":
            subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        else:
            subprocess.check_call(["python3", "-m", "venv", "venv"])
        
        print("✅ Virtual environment created!")

def final_instructions():
    """Provide final setup instructions."""
    clear_screen()
    print("🎉 The Everything Bot - Setup Complete! 🎉")
    print("----------------------------------------")
    print("To run the bot:")
    
    if platform.system() == "Windows":
        print("1. Activate the virtual environment:")
        print("   venv\\Scripts\\activate")
        print("2. Run the bot:")
        print("   python run.py")
    else:
        print("1. Activate the virtual environment:")
        print("   source venv/bin/activate")
        print("2. Run the bot:")
        print("   python3 run.py")
    
    print("\n📌 Need help? Visit our GitHub repository!")

def main():
    """Main setup process."""
    clear_screen()
    check_python_version()
    create_virtual_env()
    install_dependencies()
    generate_env_file()
    final_instructions()

if __name__ == "__main__":
    main()
