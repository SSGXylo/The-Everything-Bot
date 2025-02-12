"""
Advanced security and anti-abuse system for Discord server protection.
"""
import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from collections import defaultdict
from datetime import datetime, timedelta

from ..utils.logger import logger
from ..config import COLORS

class ServerSecurityCog(commands.Cog):
    """Advanced server protection and anti-abuse mechanisms."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_cache = defaultdict(list)
        self.spam_tracking = defaultdict(lambda: {"count": 0, "last_message_time": None})
        self.raid_protection_active = False
        self.raid_mode_users = set()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Monitor messages for potential spam and security threats.
        """
        # Ignore DMs and bot messages
        if message.guild is None or message.author.bot:
            return

        # Spam detection
        await self._check_spam(message)

        # Raid protection
        await self._check_raid_protection(message)

    async def _check_spam(self, message: discord.Message):
        """
        Detect and handle potential spam.
        """
        user_id = message.author.id
        current_time = datetime.now()

        # Track recent messages
        self.message_cache[user_id].append({
            "content": message.content,
            "timestamp": current_time
        })

        # Remove old messages (keep last 5 within 10 seconds)
        self.message_cache[user_id] = [
            msg for msg in self.message_cache[user_id] 
            if (current_time - msg['timestamp']).total_seconds() < 10
        ]

        # Check for repeated messages
        if len(self.message_cache[user_id]) > 5:
            await self._handle_spam(message)

    async def _handle_spam(self, message: discord.Message):
        """
        Take action against spam.
        """
        try:
            # Mute the user temporarily
            await message.author.timeout(
                discord.utils.utcnow() + timedelta(minutes=10), 
                reason="Spam detection"
            )

            # Delete recent messages
            await message.channel.purge(
                limit=10, 
                check=lambda m: m.author == message.author
            )

            # Notify about spam
            embed = discord.Embed(
                title="🚫 Spam Detected",
                description=f"{message.author.mention} has been muted for spam.",
                color=COLORS["error"]
            )
            await message.channel.send(embed=embed)

            logger.warning(f"Spam detected and handled for user {message.author}")
        except Exception as e:
            logger.error(f"Error handling spam: {e}")

    async def _check_raid_protection(self, message: discord.Message):
        """
        Detect and prevent potential raid attempts.
        """
        # Only activate in servers with significant member count
        if message.guild.member_count < 100:
            return

        # Check for mass join events
        join_times = [
            member.joined_at for member in message.guild.members 
            if (datetime.now(member.joined_at.tzinfo) - member.joined_at).total_seconds() < 300
        ]

        if len(join_times) > 10:  # More than 10 members joined in 5 minutes
            await self._activate_raid_mode(message.guild)

    async def _activate_raid_mode(self, guild: discord.Guild):
        """
        Activate server-wide protection during potential raid.
        """
        if self.raid_protection_active:
            return

        self.raid_protection_active = True
        
        try:
            # Disable server invites
            default_role = guild.default_role
            await default_role.edit(
                permissions=discord.Permissions(default_role.permissions.value & ~discord.Permissions.create_instant_invite)
            )

            # Slow mode in all text channels
            for channel in guild.text_channels:
                await channel.edit(slowmode_delay=10)

            # Notify admins
            admin_channel = discord.utils.get(guild.text_channels, name="admin-logs")
            if admin_channel:
                embed = discord.Embed(
                    title="🚨 Raid Protection Activated",
                    description="Potential raid detected. Server protection measures engaged.",
                    color=COLORS["error"]
                )
                await admin_channel.send(embed=embed)

            # Auto-deactivate after 30 minutes
            await asyncio.sleep(1800)
            await self._deactivate_raid_mode(guild)

        except Exception as e:
            logger.error(f"Error in raid protection: {e}")

    async def _deactivate_raid_mode(self, guild: discord.Guild):
        """
        Deactivate raid protection mode.
        """
        if not self.raid_protection_active:
            return

        try:
            # Restore server invites
            default_role = guild.default_role
            await default_role.edit(
                permissions=discord.Permissions(default_role.permissions.value | discord.Permissions.create_instant_invite)
            )

            # Remove slow mode
            for channel in guild.text_channels:
                await channel.edit(slowmode_delay=0)

            # Notify admins
            admin_channel = discord.utils.get(guild.text_channels, name="admin-logs")
            if admin_channel:
                embed = discord.Embed(
                    title="✅ Raid Protection Deactivated",
                    description="Raid protection measures have been lifted.",
                    color=COLORS["success"]
                )
                await admin_channel.send(embed=embed)

            self.raid_protection_active = False
        except Exception as e:
            logger.error(f"Error deactivating raid protection: {e}")

    @app_commands.command(name="anti_nuke_settings")
    @app_commands.default_permissions(administrator=True)
    async def anti_nuke_settings(self, interaction: discord.Interaction):
        """
        Display and configure anti-nuke settings.
        """
        embed = discord.Embed(
            title="🛡️ Anti-Nuke Protection Settings",
            description="Current server protection status and settings.",
            color=COLORS["info"]
        )
        embed.add_field(
            name="Raid Protection", 
            value="Active" if self.raid_protection_active else "Inactive"
        )
        embed.add_field(
            name="Spam Detection", 
            value="Enabled"
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Set up the Security cog."""
    await bot.add_cog(ServerSecurityCog(bot))
