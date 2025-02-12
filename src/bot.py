import os
import sys
import logging
import asyncio
import traceback

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import configuration
from src.config import (
    BOT_TOKEN, 
    COMMAND_PREFIX, 
    BOT_ACTIVITY, 
    LOG_LEVEL, 
    LOG_FILE
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('bot')

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class TheEverythingBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=COMMAND_PREFIX, 
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )
        self.initial_extensions = [
            'src.cogs.leveling',
            'src.cogs.welcome',
            'src.cogs.moderation',
            'src.cogs.security',
            'src.cogs.tickets',
            'src.cogs.games'
        ]

    async def setup_hook(self):
        """Set up bot extensions and sync commands."""
        # Load extensions
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded extension {ext}")
            except Exception as e:
                logger.error(f"Failed to load extension {ext}: {e}")
                traceback.print_exc()

        # Sync application commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} application commands")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'{self.user} has connected to Discord!')
        
        # Set bot activity
        activity = discord.Activity(
            type=discord.ActivityType.watching, 
            name=BOT_ACTIVITY
        )
        await self.change_presence(activity=activity)

def main():
    """Main bot initialization and run method."""
    # Validate token
    if not BOT_TOKEN:
        logger.critical("No Discord token found. Please set DISCORD_TOKEN in .env")
        sys.exit(1)

    # Initialize and run bot
    bot = TheEverythingBot()
    
    try:
        asyncio.run(bot.start(BOT_TOKEN))
    except KeyboardInterrupt:
        asyncio.run(bot.close())
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()
