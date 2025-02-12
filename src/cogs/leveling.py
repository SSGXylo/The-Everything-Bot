"""
Leveling system to reward active members with XP and roles.
"""
import discord
from discord.ext import commands
from discord import app_commands
import json
from pathlib import Path
import random
import asyncio
from datetime import datetime, timedelta
from ..utils.logger import logger
from ..config import COLORS

class LevelingCog(commands.Cog):
    """Experience and leveling system."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data_file = Path("data/leveling.json")
        self.config_file = Path("data/leveling_config.json")
        self.data = self._load_data()
        self.config = self._load_config()
        self.cooldowns = {}

    def _load_data(self) -> dict:
        """Load leveling data."""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_data(self):
        """Save leveling data."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)

    def _load_config(self) -> dict:
        """Load leveling configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_config(self):
        """Save leveling configuration."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def _calculate_xp(self, level: int) -> int:
        """Calculate XP needed for next level."""
        return 5 * (level ** 2) + 50 * level + 100

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle message XP rewards."""
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        # Check if leveling is enabled for this guild
        if guild_id not in self.config or not self.config[guild_id].get('enabled', False):
            return

        # Check cooldown
        cooldown_key = f"{guild_id}-{user_id}"
        if cooldown_key in self.cooldowns:
            if datetime.now() < self.cooldowns[cooldown_key]:
                return
        
        # Initialize data structures
        if guild_id not in self.data:
            self.data[guild_id] = {}
        if user_id not in self.data[guild_id]:
            self.data[guild_id][user_id] = {"xp": 0, "level": 0}

        # Award XP
        xp_gain = random.randint(15, 25)
        self.data[guild_id][user_id]["xp"] += xp_gain

        # Check for level up
        current_xp = self.data[guild_id][user_id]["xp"]
        current_level = self.data[guild_id][user_id]["level"]
        xp_required = self._calculate_xp(current_level)

        if current_xp >= xp_required:
            self.data[guild_id][user_id]["level"] += 1
            self.data[guild_id][user_id]["xp"] = current_xp - xp_required

            # Level up announcement
            if self.config[guild_id].get('announce_levelup', True):
                embed = discord.Embed(
                    title="🎉 Level Up!",
                    description=f"Congratulations {message.author.mention}! You've reached level {current_level + 1}!",
                    color=COLORS["success"]
                )
                await message.channel.send(embed=embed)

            # Check for role rewards
            if 'role_rewards' in self.config[guild_id]:
                for role_id, level_req in self.config[guild_id]['role_rewards'].items():
                    if current_level + 1 >= level_req:
                        role = message.guild.get_role(int(role_id))
                        if role and role not in message.author.roles:
                            await message.author.add_roles(role)

        # Set cooldown
        self.cooldowns[cooldown_key] = datetime.now() + timedelta(minutes=1)
        self._save_data()

    @app_commands.command(name="rank")
    async def rank(self, interaction: discord.Interaction, member: discord.Member = None):
        """
        Check your or another member's rank.
        
        Args:
            interaction: The interaction that triggered the command
            member: Optional member to check rank for
        """
        member = member or interaction.user
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        if guild_id not in self.data or user_id not in self.data[guild_id]:
            await interaction.response.send_message(
                f"{member.display_name} hasn't earned any XP yet!",
                ephemeral=True
            )
            return

        user_data = self.data[guild_id][user_id]
        current_xp = user_data["xp"]
        current_level = user_data["level"]
        xp_required = self._calculate_xp(current_level)

        # Calculate rank
        sorted_users = sorted(
            self.data[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )
        rank = next(i for i, (id, _) in enumerate(sorted_users, 1) if id == user_id)

        embed = discord.Embed(
            title=f"Rank - {member.display_name}",
            color=COLORS["primary"]
        )
        embed.add_field(name="Rank", value=f"#{rank}", inline=True)
        embed.add_field(name="Level", value=str(current_level), inline=True)
        embed.add_field(
            name="XP Progress",
            value=f"{current_xp}/{xp_required} XP",
            inline=True
        )
        embed.set_thumbnail(url=member.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """Display the server's XP leaderboard."""
        guild_id = str(interaction.guild.id)

        if guild_id not in self.data:
            await interaction.response.send_message(
                "No XP data found for this server!",
                ephemeral=True
            )
            return

        # Sort users by level and XP
        sorted_users = sorted(
            self.data[guild_id].items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )[:10]  # Top 10

        embed = discord.Embed(
            title="🏆 XP Leaderboard",
            color=COLORS["primary"]
        )

        for i, (user_id, data) in enumerate(sorted_users, 1):
            member = interaction.guild.get_member(int(user_id))
            if member:
                embed.add_field(
                    name=f"#{i} {member.display_name}",
                    value=f"Level {data['level']} • {data['xp']} XP",
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="levelconfig")
    @app_commands.default_permissions(administrator=True)
    async def level_config(self, interaction: discord.Interaction, 
                         enabled: bool = None,
                         announce_levelup: bool = None):
        """
        Configure the leveling system.
        
        Args:
            interaction: The interaction that triggered the command
            enabled: Enable or disable the leveling system
            announce_levelup: Enable or disable level up announcements
        """
        guild_id = str(interaction.guild.id)

        if guild_id not in self.config:
            self.config[guild_id] = {}

        if enabled is not None:
            self.config[guild_id]['enabled'] = enabled
        if announce_levelup is not None:
            self.config[guild_id]['announce_levelup'] = announce_levelup

        self._save_config()

        embed = discord.Embed(
            title="⚙️ Leveling System Configuration",
            color=COLORS["success"]
        )
        embed.add_field(
            name="System Enabled",
            value="✅ Yes" if self.config[guild_id].get('enabled', False) else "❌ No",
            inline=True
        )
        embed.add_field(
            name="Level Up Announcements",
            value="✅ Enabled" if self.config[guild_id].get('announce_levelup', True) else "❌ Disabled",
            inline=True
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addrole_reward")
    @app_commands.default_permissions(administrator=True)
    async def add_role_reward(self, interaction: discord.Interaction,
                            role: discord.Role,
                            level: int):
        """
        Add a role reward for reaching a specific level.
        
        Args:
            interaction: The interaction that triggered the command
            role: The role to award
            level: The level required to earn the role
        """
        guild_id = str(interaction.guild.id)

        if guild_id not in self.config:
            self.config[guild_id] = {}
        if 'role_rewards' not in self.config[guild_id]:
            self.config[guild_id]['role_rewards'] = {}

        self.config[guild_id]['role_rewards'][str(role.id)] = level
        self._save_config()

        embed = discord.Embed(
            title="✅ Role Reward Added",
            description=f"{role.mention} will be awarded at level {level}",
            color=COLORS["success"]
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    """Set up the Leveling cog."""
    await bot.add_cog(LevelingCog(bot))
