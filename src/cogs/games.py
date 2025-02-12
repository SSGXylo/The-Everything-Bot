"""
Interactive Discord games for server entertainment.
"""
import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

from ..utils.logger import logger
from ..config import COLORS

class GamesCog(commands.Cog):
    """Collection of interactive Discord games."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ongoing_games = {}

    @app_commands.command(name="rps")
    async def rock_paper_scissors(self, interaction: discord.Interaction):
        """
        Play Rock Paper Scissors against the bot.
        
        Args:
            interaction: The interaction that triggered the game
        """
        view = RPSView(interaction.user)
        await interaction.response.send_message(
            "Let's play Rock Paper Scissors! Choose your move:",
            view=view,
            ephemeral=False
        )

    @app_commands.command(name="guess")
    async def number_guessing(self, interaction: discord.Interaction, max_number: int = 100):
        """
        Start a number guessing game.
        
        Args:
            interaction: The interaction that triggered the game
            max_number: The maximum number to guess (default 100)
        """
        max_number = max(10, min(max_number, 1000))  # Limit between 10 and 1000
        secret_number = random.randint(1, max_number)
        
        embed = discord.Embed(
            title="🔢 Number Guessing Game",
            description=f"Guess a number between 1 and {max_number}!",
            color=COLORS["primary"]
        )
        
        view = NumberGuessingView(interaction.user, secret_number, max_number)
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=False
        )

    @app_commands.command(name="trivia")
    async def trivia(self, interaction: discord.Interaction):
        """
        Start a trivia game.
        
        Args:
            interaction: The interaction that triggered the game
        """
        trivia_question = self._get_random_trivia_question()
        view = TriviaView(interaction.user, trivia_question)
        
        embed = discord.Embed(
            title="🤔 Trivia Challenge",
            description=trivia_question['question'],
            color=COLORS["info"]
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=False
        )

    def _get_random_trivia_question(self) -> dict:
        """
        Generate a random trivia question.
        
        Returns:
            dict: A trivia question with options
        """
        trivia_questions = [
            {
                "question": "What is the capital of France?",
                "options": ["London", "Berlin", "Paris", "Rome"],
                "correct": "Paris"
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct": "Mars"
            },
            {
                "question": "Who painted the Mona Lisa?",
                "options": ["Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Claude Monet"],
                "correct": "Leonardo da Vinci"
            }
        ]
        return random.choice(trivia_questions)

class RPSView(discord.ui.View):
    """View for Rock Paper Scissors game."""
    
    def __init__(self, player: discord.Member):
        super().__init__()
        self.player = player

    @discord.ui.button(label="✊ Rock", style=discord.ButtonStyle.primary)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._play_rps(interaction, "rock")

    @discord.ui.button(label="✋ Paper", style=discord.ButtonStyle.primary)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._play_rps(interaction, "paper")

    @discord.ui.button(label="✌️ Scissors", style=discord.ButtonStyle.primary)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._play_rps(interaction, "scissors")

    async def _play_rps(self, interaction: discord.Interaction, player_choice: str):
        # Check if the interaction user is the original player
        if interaction.user != self.player:
            await interaction.response.send_message(
                "This is not your game!", 
                ephemeral=True
            )
            return

        # Bot's choice
        choices = ["rock", "paper", "scissors"]
        bot_choice = random.choice(choices)

        # Determine winner
        result = self._determine_winner(player_choice, bot_choice)

        # Create result embed
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            color=COLORS["primary"]
        )
        embed.add_field(name="Your Choice", value=player_choice.capitalize(), inline=True)
        embed.add_field(name="Bot's Choice", value=bot_choice.capitalize(), inline=True)
        
        if result == "tie":
            embed.description = "It's a tie! 🤝"
            embed.color = COLORS["info"]
        elif result == "win":
            embed.description = "You win! 🎉"
            embed.color = COLORS["success"]
        else:
            embed.description = "Bot wins! 🤖"
            embed.color = COLORS["error"]

        # Respond and disable buttons
        await interaction.response.edit_message(embed=embed, view=None)

    def _determine_winner(self, player: str, bot: str) -> str:
        """
        Determine the winner of Rock Paper Scissors.
        
        Returns:
            str: 'win', 'lose', or 'tie'
        """
        if player == bot:
            return "tie"
        
        winning_combos = {
            "rock": "scissors",
            "paper": "rock",
            "scissors": "paper"
        }
        
        return "win" if winning_combos[player] == bot else "lose"

class NumberGuessingView(discord.ui.View):
    """View for Number Guessing game."""
    
    def __init__(self, player: discord.Member, secret_number: int, max_number: int):
        super().__init__()
        self.player = player
        self.secret_number = secret_number
        self.max_number = max_number
        self.attempts = 0
        self.max_attempts = 10

    @discord.ui.button(label="Guess", style=discord.ButtonStyle.primary)
    async def guess_number(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Check if the interaction user is the original player
        if interaction.user != self.player:
            await interaction.response.send_message(
                "This is not your game!", 
                ephemeral=True
            )
            return

        # Prompt for number input
        await interaction.response.send_modal(NumberGuessingModal(self))

class NumberGuessingModal(discord.ui.Modal):
    """Modal for number input in Number Guessing game."""
    
    def __init__(self, view: NumberGuessingView):
        super().__init__(title="Guess the Number")
        self.view = view
        
        self.number = discord.ui.TextInput(
            label=f"Enter a number (1-{self.view.max_number})",
            placeholder=f"Guess a number between 1 and {self.view.max_number}",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.number)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            guess = int(self.number.value)
            self.view.attempts += 1

            # Create result embed
            embed = discord.Embed(
                title="🔢 Number Guessing Game",
                color=COLORS["primary"]
            )

            if guess < 1 or guess > self.view.max_number:
                embed.description = f"Invalid guess! Please enter a number between 1 and {self.view.max_number}."
                embed.color = COLORS["warning"]
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            if guess == self.view.secret_number:
                embed.description = f"🎉 Congratulations! You guessed the number {self.view.secret_number} in {self.view.attempts} attempts!"
                embed.color = COLORS["success"]
                await interaction.response.edit_message(embed=embed, view=None)
            elif self.view.attempts >= self.view.max_attempts:
                embed.description = f"Game Over! The number was {self.view.secret_number}."
                embed.color = COLORS["error"]
                await interaction.response.edit_message(embed=embed, view=None)
            else:
                hint = "higher" if guess < self.view.secret_number else "lower"
                remaining = self.view.max_attempts - self.view.attempts
                embed.description = f"Wrong guess! Try a {hint} number. {remaining} attempts remaining."
                await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid number!", 
                ephemeral=True
            )

class TriviaView(discord.ui.View):
    """View for Trivia game."""
    
    def __init__(self, player: discord.Member, question: dict):
        super().__init__()
        self.player = player
        self.question = question
        
        # Shuffle options
        options = question['options'].copy()
        random.shuffle(options)
        
        # Create buttons for each option
        for option in options:
            self.add_item(
                discord.ui.Button(
                    label=option, 
                    style=discord.ButtonStyle.primary,
                    custom_id=option
                )
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the interaction is from the original player."""
        if interaction.user != self.player:
            await interaction.response.send_message(
                "This is not your game!", 
                ephemeral=True
            )
            return False
        return True

    async def callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle button click for trivia game."""
        embed = discord.Embed(title="🤔 Trivia Challenge")
        
        if button.label == self.question['correct']:
            embed.description = "✅ Correct answer! Well done!"
            embed.color = COLORS["success"]
        else:
            embed.description = f"❌ Wrong answer! The correct answer was {self.question['correct']}."
            embed.color = COLORS["error"]
        
        # Disable all buttons after answer
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot: commands.Bot):
    """Set up the Games cog."""
    await bot.add_cog(GamesCog(bot))
