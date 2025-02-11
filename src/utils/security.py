"""
Security utilities for the Discord Ticket Bot.
"""
import re
from typing import Optional
from datetime import datetime, timedelta
from collections import defaultdict
import discord
from ..config import COLORS
from .logger import logger

class RateLimiter:
    """Rate limiting implementation for commands and actions."""
    
    def __init__(self):
        self._command_usage = defaultdict(list)
        self._ticket_creation = defaultdict(list)
    
    def _cleanup_old_entries(self, entries: list, window: int):
        """Remove entries older than the time window."""
        current_time = datetime.now()
        return [time for time in entries if current_time - time < timedelta(seconds=window)]

    def can_create_ticket(self, user_id: int) -> tuple[bool, Optional[int]]:
        """
        Check if a user can create a ticket.
        
        Args:
            user_id: The Discord user ID
            
        Returns:
            tuple[bool, Optional[int]]: (can_create, cooldown_remaining)
        """
        WINDOW = 3600  # 1 hour
        MAX_TICKETS = 3
        
        # Cleanup old entries
        self._ticket_creation[user_id] = self._cleanup_old_entries(
            self._ticket_creation[user_id],
            WINDOW
        )
        
        # Check rate limit
        if len(self._ticket_creation[user_id]) >= MAX_TICKETS:
            oldest_time = min(self._ticket_creation[user_id])
            cooldown = int((oldest_time + timedelta(seconds=WINDOW) - datetime.now()).total_seconds())
            return False, cooldown
        
        # Add new entry
        self._ticket_creation[user_id].append(datetime.now())
        return True, None

    def check_rate_limit(self, user_id: int, command: str) -> tuple[bool, Optional[int]]:
        """
        Check if a command is rate limited.
        
        Args:
            user_id: The Discord user ID
            command: The command being used
            
        Returns:
            tuple[bool, Optional[int]]: (allowed, cooldown_remaining)
        """
        LIMITS = {
            "default": (5, 60),    # 5 commands per minute
            "setup": (3, 3600),    # 3 setups per hour
            "stats": (10, 60),     # 10 stats checks per minute
        }
        
        limit, window = LIMITS.get(command, LIMITS["default"])
        key = f"{user_id}:{command}"
        
        # Cleanup old entries
        self._command_usage[key] = self._cleanup_old_entries(
            self._command_usage[key],
            window
        )
        
        # Check rate limit
        if len(self._command_usage[key]) >= limit:
            oldest_time = min(self._command_usage[key])
            cooldown = int((oldest_time + timedelta(seconds=window) - datetime.now()).total_seconds())
            return False, cooldown
            
        # Add new entry
        self._command_usage[key].append(datetime.now())
        return True, None

class SecurityValidator:
    """Input validation and security checks."""
    
    @staticmethod
    def is_safe_channel_name(name: str) -> bool:
        """
        Validate channel name for safety.
        
        Args:
            name: The channel name to validate
            
        Returns:
            bool: True if safe, False otherwise
        """
        # Only allow lowercase letters, numbers, and hyphens
        return bool(re.match(r'^[a-z0-9-]+$', name))
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """
        Sanitize user input text.
        
        Args:
            text: The text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            str: Sanitized text
        """
        # Remove any Discord markdown exploits
        text = re.sub(r'[`\*_~]', '', text)
        # Limit length
        return text[:max_length]
    
    @staticmethod
    async def check_permissions(interaction: discord.Interaction, required_perms: list) -> bool:
        """
        Check if user has required permissions.
        
        Args:
            interaction: The Discord interaction
            required_perms: List of required permissions
            
        Returns:
            bool: True if user has permissions, False otherwise
        """
        if interaction.guild is None:
            return False
            
        user_perms = interaction.channel.permissions_for(interaction.user)
        return all(getattr(user_perms, perm, False) for perm in required_perms)

async def handle_error(interaction: discord.Interaction, error: Exception) -> None:
    """
    Handle errors securely.
    
    Args:
        interaction: The Discord interaction
        error: The error that occurred
    """
    # Log the error securely
    logger.error(f"Error in {interaction.command}: {str(error)}")
    
    # Generic error message to user (avoid exposing sensitive info)
    embed = discord.Embed(
        title="❌ Error",
        description="An error occurred while processing your request. Please try again later.",
        color=COLORS["error"]
    )
    
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Error sending error message: {e}")

# Global instances
rate_limiter = RateLimiter()
validator = SecurityValidator()
