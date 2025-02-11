"""
Main bot implementation file.
"""
import discord
from discord.ext import commands
import asyncio
import sys
from pathlib import Path

from .config import BOT_TOKEN, COMMAND_PREFIX
from .utils.logger import logger

class TicketBot(commands.Bot):
    """Custom bot class with additional functionality."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        
        super().__init__(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for tickets 🎫"
            )
        )
    
    async def setup_hook(self):
        """Set up the bot's cogs and sync commands."""
        # Load cogs
        cogs_dir = Path(__file__).parent / "cogs"
        for cog_file in cogs_dir.glob("*.py"):
            if cog_file.stem != "__init__":
                try:
                    await self.load_extension(f"src.cogs.{cog_file.stem}")
                    logger.info(f"Loaded cog: {cog_file.stem}")
                except Exception as e:
                    logger.error(f"Failed to load cog {cog_file.stem}: {e}")
        
        # Sync commands
        try:
            logger.info("Syncing commands...")
            await self.tree.sync()
            logger.info("Commands synced successfully!")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info("------")

async def main():
    """Main entry point for the bot."""
    async with TicketBot() as bot:
        if not BOT_TOKEN:
            logger.error("No bot token found! Please set the DISCORD_TOKEN environment variable.")
            return
        
        try:
            await bot.start(BOT_TOKEN)
        except discord.LoginFailure:
            logger.error("Failed to login. Please check your bot token.")
        except Exception as e:
            logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown by user")
        sys.exit(0)
