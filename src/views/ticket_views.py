"""
Discord UI views for ticket management.
"""
import discord
from discord import ui
from ..config import COLORS, TICKET_CREATED_MESSAGE, TICKET_CLOSED_MESSAGE
from ..database.ticket_manager import TicketManager
from ..utils.logger import logger

class TicketView(ui.View):
    """View for the ticket creation button."""
    
    def __init__(self):
        super().__init__(timeout=None)
        self.ticket_manager = TicketManager()

    @ui.button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
        """Handle ticket creation button click."""
        try:
            # Check for existing ticket
            if self.ticket_manager.get_user_open_ticket(interaction.user.id):
                await interaction.response.send_message(
                    "You already have an open ticket!",
                    ephemeral=True
                )
                return

            # Create ticket category if it doesn't exist
            category = discord.utils.get(interaction.guild.categories, name="Tickets")
            if not category:
                category = await interaction.guild.create_category("Tickets")

            # Generate ticket number and create channel
            ticket_number = len(self.ticket_manager.tickets) + 1
            channel_name = f"ticket-{ticket_number}"

            # Set up channel permissions
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }

            # Add support role permissions if it exists
            support_role = discord.utils.get(interaction.guild.roles, name="Support Team")
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            # Create the channel
            channel = await category.create_text_channel(
                channel_name,
                overwrites=overwrites
            )

            # Store ticket in database
            self.ticket_manager.create_ticket(
                str(ticket_number),
                interaction.user.id,
                channel.id
            )

            # Create and send the initial embed
            embed = discord.Embed(
                title=f"Ticket #{ticket_number}",
                description=TICKET_CREATED_MESSAGE,
                color=COLORS["primary"]
            )
            embed.set_footer(text=f"Opened by {interaction.user.name}")

            # Send the initial message with close button
            await channel.send(
                embed=embed,
                view=TicketCloseView(self.ticket_manager)
            )

            # Confirm to user
            await interaction.response.send_message(
                f"Created ticket channel: {channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            await interaction.response.send_message(
                "An error occurred while creating your ticket. Please try again later.",
                ephemeral=True
            )

class TicketCloseView(ui.View):
    """View for the ticket close button."""
    
    def __init__(self, ticket_manager: TicketManager):
        super().__init__(timeout=None)
        self.ticket_manager = ticket_manager

    @ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        """Handle ticket close button click."""
        try:
            channel = interaction.channel
            
            # Find ticket number from channel name
            ticket_number = channel.name.split('-')[1]
            
            # Close ticket in database
            if self.ticket_manager.close_ticket(ticket_number, interaction.user.id):
                await channel.send(TICKET_CLOSED_MESSAGE)
                await discord.asyncio.sleep(5)
                await channel.delete()
            else:
                await interaction.response.send_message(
                    "This ticket has already been closed.",
                    ephemeral=True
                )

        except Exception as e:
            logger.error(f"Error closing ticket: {e}")
            await interaction.response.send_message(
                "An error occurred while closing the ticket. Please try again later.",
                ephemeral=True
            )
