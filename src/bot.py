import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Ticket data structure
TICKETS_FILE = 'tickets.json'

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=4)

tickets = load_tickets()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if user already has an open ticket
        for ticket_id, ticket_info in tickets.items():
            if ticket_info["user_id"] == interaction.user.id and not ticket_info["closed"]:
                await interaction.response.send_message("You already have an open ticket!", ephemeral=True)
                return

        # Create new ticket channel
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="Tickets")
        
        if not category:
            category = await guild.create_category("Tickets")

        ticket_number = len(tickets) + 1
        channel_name = f"ticket-{ticket_number}"
        
        # Set permissions for the ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }

        channel = await category.create_text_channel(channel_name, overwrites=overwrites)
        
        # Store ticket information
        tickets[str(ticket_number)] = {
            "channel_id": channel.id,
            "user_id": interaction.user.id,
            "created_at": datetime.now().isoformat(),
            "closed": False
        }
        save_tickets(tickets)

        # Send initial message in ticket channel
        embed = discord.Embed(
            title=f"Ticket #{ticket_number}",
            description="Support will be with you shortly. Please describe your issue.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Opened by {interaction.user.name}")
        
        close_view = TicketCloseView()
        await channel.send(embed=embed, view=close_view)
        
        await interaction.response.send_message(f"Created ticket channel: {channel.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.channel
        
        # Find ticket number
        ticket_number = None
        for num, info in tickets.items():
            if info["channel_id"] == channel.id:
                ticket_number = num
                break
        
        if ticket_number:
            tickets[ticket_number]["closed"] = True
            save_tickets(tickets)
            
            await channel.send("This ticket will be closed in 5 seconds...")
            await discord.asyncio.sleep(5)
            await channel.delete()

@bot.tree.command(name="setup", description="Setup the ticket system")
@app_commands.default_permissions(administrator=True)
async def setup(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 Support Ticket System",
        description="Click the button below to create a support ticket",
        color=discord.Color.blue()
    )
    
    view = TicketView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("Ticket system has been set up!", ephemeral=True)

# Run the bot
bot.run(os.getenv('DISCORD_TOKEN'))
