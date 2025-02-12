"""
Centralized configuration management for The Everything Bot.
Loads settings from environment variables with sensible defaults.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Color palette for embeds and UI
COLORS = {
    "primary": 0x3498db,   # Blue
    "success": 0x2ecc71,   # Green
    "warning": 0xf39c12,   # Orange
    "error": 0xe74c3c,     # Red
    "info": 0x9b59b6       # Purple
}

# Bot Configuration
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('BOT_PREFIX', '/')
BOT_ACTIVITY = os.getenv('BOT_ACTIVITY', 'Helping servers!')

# Security Settings
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'auto_generate')
ALLOWED_GUILDS = [int(guild) for guild in os.getenv('ALLOWED_GUILDS', '').split(',') if guild]

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'logs/bot.log')

# Feature Toggles
LEVELING_ENABLED = os.getenv('LEVELING_ENABLED', 'true').lower() == 'true'
WELCOME_SYSTEM_ENABLED = os.getenv('WELCOME_SYSTEM_ENABLED', 'true').lower() == 'true'

# Moderation Settings
DEFAULT_MUTE_ROLE = os.getenv('DEFAULT_MUTE_ROLE')
MODERATION_LOGS_CHANNEL = os.getenv('MODERATION_LOGS_CHANNEL')

# Ticket System Settings
TICKET_CATEGORY = os.getenv('TICKET_CATEGORY')
TICKET_SUPPORT_ROLE = os.getenv('TICKET_SUPPORT_ROLE')

# Validate critical configurations
def validate_config():
    """Validate critical bot configurations."""
    errors = []
    
    if not BOT_TOKEN:
        errors.append("Discord bot token is missing")
    
    return errors

# Optional: Validate on import
config_errors = validate_config()
if config_errors:
    raise ValueError(f"Configuration errors: {', '.join(config_errors)}")
