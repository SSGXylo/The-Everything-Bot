"""
Welcome system for new members with customizable messages and auto-role assignment.
"""
import discord
from discord.ext import commands
from discord import app_commands
import json
from pathlib import Path
from ..utils.logger import logger
from ..config import COLORS

class WelcomeCog(commands.Cog):
    """Welcome message and auto-role system."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config_file = Path("data/welcome_config.json")
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load welcome configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_config(self):
        """Save welcome configuration."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle new member joins."""
        guild_id = str(member.guild.id)
        if guild_id not in self.config:
            return

        config = self.config[guild_id]

        # Send welcome message
        if 'welcome_channel_id' in config:
            try:
                channel = member.guild.get_channel(config['welcome_channel_id'])
                if channel:
                    embed = discord.Embed(
                        title="👋 Welcome!",
                        description=config.get('welcome_message', '').format(
                            member=member.mention,
                            server=member.guild.name
                        ),
                        color=COLORS["primary"]
                    )
                    embed.set_thumbnail(url=member.display_avatar.url)
                    await channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Error sending welcome message: {e}")

        # Assign auto-role
        if 'auto_role_id' in config:
            try:
                role = member.guild.get_role(config['auto_role_id'])
                if role:
                    await member.add_roles(role, reason="Auto-role assignment")
            except Exception as e:
                logger.error(f"Error assigning auto-role: {e}")

    @app_commands.command(name="welcome_setup")
    @app_commands.default_permissions(administrator=True)
    async def welcome_setup(self, interaction: discord.Interaction, 
                          channel: discord.TextChannel,
                          auto_role: discord.Role = None):
        """
        Set up the welcome system.
        
        Args:
            interaction: The interaction that triggered the command
            channel: The channel for welcome messages
            auto_role: Optional role to automatically assign to new members
        """
        guild_id = str(interaction.guild.id)
        
        # Create modal for welcome message
        await interaction.response.send_modal(
            WelcomeMessageModal(self, channel, auto_role)
        )

    @app_commands.command(name="welcome_test")
    @app_commands.default_permissions(administrator=True)
    async def welcome_test(self, interaction: discord.Interaction):
        """Test the welcome message with your own profile."""
        guild_id = str(interaction.guild.id)
        if guild_id not in self.config:
            await interaction.response.send_message(
                "Welcome system is not set up yet! Use `/welcome_setup` first.",
                ephemeral=True
            )
            return

        # Simulate welcome message
        config = self.config[guild_id]
        if 'welcome_channel_id' in config:
            channel = interaction.guild.get_channel(config['welcome_channel_id'])
            if channel:
                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=config.get('welcome_message', '').format(
                        member=interaction.user.mention,
                        server=interaction.guild.name
                    ),
                    color=COLORS["primary"]
                )
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                await interaction.response.send_message(
                    "Sending test welcome message...",
                    ephemeral=True
                )
                await channel.send(embed=embed)
            else:
                await interaction.response.send_message(
                    "Welcome channel not found!",
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(
                "Welcome channel not configured!",
                ephemeral=True
            )

class WelcomeMessageModal(discord.ui.Modal):
    """Modal for setting up welcome message."""

    def __init__(self, cog: WelcomeCog, channel: discord.TextChannel, auto_role: discord.Role):
        super().__init__(title="Welcome Message Setup")
        self.cog = cog
        self.channel = channel
        self.auto_role = auto_role

        self.message = discord.ui.TextInput(
            label="Welcome Message",
            style=discord.TextStyle.paragraph,
            placeholder="Welcome {member} to {server}! 🎉",
            default=self.cog.config.get(str(channel.guild.id), {}).get(
                'welcome_message',
                "Welcome {member} to {server}! 🎉\nWe're glad to have you here!"
            ),
            required=True,
            max_length=1000
        )
        self.add_item(self.message)

    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        guild_id = str(interaction.guild.id)
        
        # Save configuration
        self.cog.config[guild_id] = {
            'welcome_channel_id': self.channel.id,
            'welcome_message': self.message.value
        }
        
        if self.auto_role:
            self.cog.config[guild_id]['auto_role_id'] = self.auto_role.id
            
        self.cog._save_config()

        # Send confirmation
        embed = discord.Embed(
            title="✅ Welcome System Configured",
            color=COLORS["success"]
        )
        embed.add_field(
            name="Welcome Channel",
            value=self.channel.mention,
            inline=False
        )
        if self.auto_role:
            embed.add_field(
                name="Auto-Role",
                value=self.auto_role.mention,
                inline=False
            )
        embed.add_field(
            name="Welcome Message",
            value=self.message.value.format(
                member=interaction.user.mention,
                server=interaction.guild.name
            ),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    """Set up the Welcome cog."""
    await bot.add_cog(WelcomeCog(bot))
