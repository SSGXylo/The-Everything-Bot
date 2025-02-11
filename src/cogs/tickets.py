"""
Ticket management commands and event handlers.
"""
import discord
from discord import app_commands
from discord.ext import commands
from ..views.ticket_views import TicketView
from ..database.ticket_manager import TicketManager
from ..config import COLORS
from ..utils.logger import logger

class TicketCog(commands.Cog):
    """Ticket system commands and functionality."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ticket_manager = TicketManager()

    @app_commands.command(name="setup")
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """Set up the ticket system in the current channel."""
        try:
            embed = discord.Embed(
                title="🎫 Support Ticket System",
                description=(
                    "Need help? Click the button below to create a support ticket!\n\n"
                    "Our support team will assist you as soon as possible."
                ),
                color=COLORS["primary"]
            )
            
            view = TicketView()
            await interaction.channel.send(embed=embed, view=view)
            await interaction.response.send_message(
                "Ticket system has been set up successfully!",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Error in setup command: {e}")
            await interaction.response.send_message(
                "An error occurred while setting up the ticket system.",
                ephemeral=True
            )

    @app_commands.command(name="stats")
    @app_commands.default_permissions(administrator=True)
    async def stats(self, interaction: discord.Interaction):
        """View ticket statistics."""
        try:
            stats = self.ticket_manager.get_ticket_stats()
            
            embed = discord.Embed(
                title="📊 Ticket Statistics",
                color=COLORS["info"]
            )
            embed.add_field(name="Total Tickets", value=stats["total"])
            embed.add_field(name="Open Tickets", value=stats["open"])
            embed.add_field(name="Closed Tickets", value=stats["closed"])
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await interaction.response.send_message(
                "An error occurred while fetching ticket statistics.",
                ephemeral=True
            )

    @app_commands.command(name="mytickets")
    async def my_tickets(self, interaction: discord.Interaction):
        """View your ticket history."""
        try:
            tickets = self.ticket_manager.get_user_tickets(interaction.user.id)
            
            if not tickets:
                await interaction.response.send_message(
                    "You haven't created any tickets yet.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🎫 Your Tickets",
                color=COLORS["info"]
            )
            
            for ticket in tickets:
                status = "🔴 Closed" if ticket["closed"] else "🟢 Open"
                value = f"Status: {status}\nCreated: <t:{int(ticket['created_at'])}:R>"
                
                if ticket["closed"] and ticket["closed_at"]:
                    value += f"\nClosed: <t:{int(ticket['closed_at'])}:R>"
                
                embed.add_field(
                    name=f"Ticket #{ticket['ticket_id']}",
                    value=value,
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in mytickets command: {e}")
            await interaction.response.send_message(
                "An error occurred while fetching your tickets.",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Set up the Tickets cog."""
    await bot.add_cog(TicketCog(bot))
