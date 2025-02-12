"""
Moderation commands and utilities for the Discord bot.
"""
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime, timedelta

from ..utils.logger import logger
from ..config import COLORS

class ModerationCog(commands.Cog):
    """Moderation commands for managing server safety."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._muted_users = {}

    @app_commands.command(name="kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        """
        Kick a member from the server.
        
        Args:
            interaction: The interaction that triggered the command
            member: The member to kick
            reason: Reason for the kick
        """
        try:
            # Check if the bot has permissions
            if not interaction.guild.me.guild_permissions.kick_members:
                await interaction.response.send_message(
                    "❌ I don't have permission to kick members.",
                    ephemeral=True
                )
                return

            # Check if the invoking user has higher hierarchy
            if interaction.user.top_role <= member.top_role:
                await interaction.response.send_message(
                    "❌ You cannot kick a member with an equal or higher role.",
                    ephemeral=True
                )
                return

            # Create an embed for the kick log
            embed = discord.Embed(
                title="👢 Member Kicked",
                color=COLORS["warning"]
            )
            embed.add_field(name="User", value=member.mention, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.timestamp = datetime.now()

            # Try to DM the user about the kick
            try:
                await member.send(
                    f"You have been kicked from {interaction.guild.name}. "
                    f"Reason: {reason}"
                )
            except discord.HTTPException:
                pass  # User might have DMs disabled

            # Kick the member
            await member.kick(reason=reason)

            # Send confirmation and log
            await interaction.response.send_message(
                embed=embed,
                ephemeral=False
            )
            logger.info(f"User {member} kicked by {interaction.user}. Reason: {reason}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to kick this member.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in kick command: {e}")
            await interaction.response.send_message(
                "An error occurred while trying to kick the member.",
                ephemeral=True
            )

    @app_commands.command(name="ban")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, 
                  reason: str = "No reason provided", 
                  delete_message_days: int = 0):
        """
        Ban a member from the server.
        
        Args:
            interaction: The interaction that triggered the command
            member: The member to ban
            reason: Reason for the ban
            delete_message_days: Number of days of messages to delete (0-7)
        """
        try:
            # Check if the bot has permissions
            if not interaction.guild.me.guild_permissions.ban_members:
                await interaction.response.send_message(
                    "❌ I don't have permission to ban members.",
                    ephemeral=True
                )
                return

            # Check if the invoking user has higher hierarchy
            if interaction.user.top_role <= member.top_role:
                await interaction.response.send_message(
                    "❌ You cannot ban a member with an equal or higher role.",
                    ephemeral=True
                )
                return

            # Validate delete_message_days
            delete_message_days = max(0, min(delete_message_days, 7))

            # Create an embed for the ban log
            embed = discord.Embed(
                title="🔨 Member Banned",
                color=COLORS["error"]
            )
            embed.add_field(name="User", value=member.mention, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Messages Deleted", value=f"{delete_message_days} days", inline=False)
            embed.timestamp = datetime.now()

            # Try to DM the user about the ban
            try:
                await member.send(
                    f"You have been banned from {interaction.guild.name}. "
                    f"Reason: {reason}"
                )
            except discord.HTTPException:
                pass  # User might have DMs disabled

            # Ban the member
            await member.ban(
                reason=reason, 
                delete_message_days=delete_message_days
            )

            # Send confirmation and log
            await interaction.response.send_message(
                embed=embed,
                ephemeral=False
            )
            logger.info(f"User {member} banned by {interaction.user}. Reason: {reason}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to ban this member.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in ban command: {e}")
            await interaction.response.send_message(
                "An error occurred while trying to ban the member.",
                ephemeral=True
            )

    @app_commands.command(name="mute")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, 
                   member: discord.Member, 
                   duration: str = "5m", 
                   reason: str = "No reason provided"):
        """
        Timeout/Mute a member.
        
        Args:
            interaction: The interaction that triggered the command
            member: The member to mute
            duration: Duration of mute (e.g., 1h, 30m, 1d)
            reason: Reason for the mute
        """
        try:
            # Check if the bot has permissions
            if not interaction.guild.me.guild_permissions.moderate_members:
                await interaction.response.send_message(
                    "❌ I don't have permission to mute members.",
                    ephemeral=True
                )
                return

            # Check if the invoking user has higher hierarchy
            if interaction.user.top_role <= member.top_role:
                await interaction.response.send_message(
                    "❌ You cannot mute a member with an equal or higher role.",
                    ephemeral=True
                )
                return

            # Parse duration
            duration_map = {
                's': 1, 'm': 60, 'h': 3600, 'd': 86400
            }
            try:
                amount = int(duration[:-1])
                unit = duration[-1].lower()
                if unit not in duration_map:
                    raise ValueError("Invalid duration unit")
                
                seconds = amount * duration_map[unit]
                # Discord limitation: max 28 days
                seconds = min(seconds, 28 * 86400)
                
                timeout_until = discord.utils.utcnow() + timedelta(seconds=seconds)
            except (ValueError, TypeError):
                await interaction.response.send_message(
                    "❌ Invalid duration. Use format like '5m' (5 minutes), '1h' (1 hour), '1d' (1 day).",
                    ephemeral=True
                )
                return

            # Create an embed for the mute log
            embed = discord.Embed(
                title="🔇 Member Muted",
                color=COLORS["warning"]
            )
            embed.add_field(name="User", value=member.mention, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Duration", value=duration, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.timestamp = datetime.now()

            # Mute the member
            await member.timeout(timeout_until, reason=reason)

            # Send confirmation and log
            await interaction.response.send_message(
                embed=embed,
                ephemeral=False
            )
            logger.info(f"User {member} muted by {interaction.user} for {duration}. Reason: {reason}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to mute this member.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in mute command: {e}")
            await interaction.response.send_message(
                "An error occurred while trying to mute the member.",
                ephemeral=True
            )

    @app_commands.command(name="unmute")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """
        Remove timeout/mute from a member.
        
        Args:
            interaction: The interaction that triggered the command
            member: The member to unmute
        """
        try:
            # Check if the bot has permissions
            if not interaction.guild.me.guild_permissions.moderate_members:
                await interaction.response.send_message(
                    "❌ I don't have permission to unmute members.",
                    ephemeral=True
                )
                return

            # Check if member is actually muted
            if not member.is_timed_out():
                await interaction.response.send_message(
                    "❌ This member is not currently muted.",
                    ephemeral=True
                )
                return

            # Remove timeout
            await member.timeout(None)

            # Create an embed for the unmute log
            embed = discord.Embed(
                title="🔊 Member Unmuted",
                color=COLORS["success"]
            )
            embed.add_field(name="User", value=member.mention, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.timestamp = datetime.now()

            # Send confirmation and log
            await interaction.response.send_message(
                embed=embed,
                ephemeral=False
            )
            logger.info(f"User {member} unmuted by {interaction.user}")

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to unmute this member.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in unmute command: {e}")
            await interaction.response.send_message(
                "An error occurred while trying to unmute the member.",
                ephemeral=True
            )

    @app_commands.command(name="warn")
    @app_commands.default_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, 
                   member: discord.Member, 
                   reason: str = "No reason provided"):
        """
        Issue a warning to a member.
        
        Args:
            interaction: The interaction that triggered the command
            member: The member to warn
            reason: Reason for the warning
        """
        try:
            # Create an embed for the warning
            embed = discord.Embed(
                title="⚠️ Warning Issued",
                color=COLORS["warning"]
            )
            embed.add_field(name="User", value=member.mention, inline=False)
            embed.add_field(name="Moderator", value=interaction.user.mention, inline=False)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.timestamp = datetime.now()

            # Try to DM the user about the warning
            try:
                await member.send(
                    f"You have received a warning in {interaction.guild.name}. "
                    f"Reason: {reason}"
                )
            except discord.HTTPException:
                pass  # User might have DMs disabled

            # Send confirmation and log
            await interaction.response.send_message(
                embed=embed,
                ephemeral=False
            )
            logger.info(f"Warning issued to {member} by {interaction.user}. Reason: {reason}")

        except Exception as e:
            logger.error(f"Error in warn command: {e}")
            await interaction.response.send_message(
                "An error occurred while trying to issue a warning.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Set up the Moderation cog."""
    await bot.add_cog(ModerationCog(bot))
