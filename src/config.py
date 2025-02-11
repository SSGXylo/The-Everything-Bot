"""
Configuration management for the Discord Ticket Bot.
"""
import os
import secrets
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Security Settings
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY") or secrets.token_hex(32)
MAX_TICKETS_PER_USER = 50
TICKET_CLEANUP_DAYS = 30
REQUIRED_PERMISSIONS = [
    "manage_channels",
    "manage_roles",
    "view_channel",
    "send_messages",
    "manage_messages",
    "embed_links",
    "attach_files",
    "read_message_history",
    "add_reactions"
]

# Rate Limiting
RATE_LIMITS = {
    "ticket_create": (3, 3600),    # 3 tickets per hour
    "ticket_close": (10, 3600),    # 10 closes per hour
    "command_global": (30, 60),    # 30 commands per minute
}

# Bot Configuration
COMMAND_PREFIX = "!"
BOT_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

# Ensure bot token is set
if not BOT_TOKEN:
    raise ValueError("DISCORD_TOKEN must be set in .env file")

# Ticket Configuration
TICKET_CATEGORY_NAME = "Tickets"
TICKETS_FILE = Path("data/tickets.json")
LOGS_DIR = Path("logs")
SUPPORT_ROLE_NAME = "Support Team"

# File paths and directories
DATA_DIR = Path("data")
BACKUP_DIR = DATA_DIR / "backups"

# Ensure required directories exist
for directory in [DATA_DIR, BACKUP_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Embed Colors
COLORS = {
    "primary": 0x3498db,    # Blue
    "success": 0x2ecc71,    # Green
    "warning": 0xf1c40f,    # Yellow
    "error": 0xe74c3c,      # Red
    "info": 0x95a5a6,       # Gray
}

# Message Templates
TICKET_CREATED_MESSAGE = """
Welcome to your support ticket!
Please describe your issue and a member of our support team will assist you shortly.

To help us serve you better, please provide:
• A clear description of your issue
• Any relevant screenshots or information
• Steps to reproduce (if applicable)

Note: This conversation will be logged for support purposes.
"""

TICKET_CLOSED_MESSAGE = "This ticket will be closed in 5 seconds..."

# Logging Configuration
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# Validation
MAX_TICKET_SUBJECT_LENGTH = 100
MAX_TICKET_CONTENT_LENGTH = 2000
ALLOWED_FILE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.txt', '.pdf'}
