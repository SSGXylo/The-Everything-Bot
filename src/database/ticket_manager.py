"""
Ticket management and persistence layer.
"""
import json
from datetime import datetime
from typing import Dict, Optional, List
from ..config import TICKETS_FILE
from ..utils.logger import logger

class TicketManager:
    def __init__(self):
        self.tickets = self._load_tickets()

    def _load_tickets(self) -> Dict:
        """Load tickets from the JSON file."""
        try:
            if TICKETS_FILE.exists():
                with open(TICKETS_FILE, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading tickets: {e}")
            return {}

    def _save_tickets(self) -> None:
        """Save tickets to the JSON file."""
        try:
            with open(TICKETS_FILE, 'w') as f:
                json.dump(self.tickets, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving tickets: {e}")

    def create_ticket(self, ticket_id: str, user_id: int, channel_id: int) -> None:
        """
        Create a new ticket.
        
        Args:
            ticket_id: The ID of the ticket
            user_id: The Discord user ID of the ticket creator
            channel_id: The Discord channel ID for the ticket
        """
        self.tickets[ticket_id] = {
            "channel_id": channel_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "closed": False,
            "closed_at": None,
            "closed_by": None
        }
        self._save_tickets()
        logger.info(f"Created ticket {ticket_id} for user {user_id}")

    def close_ticket(self, ticket_id: str, closed_by: int) -> bool:
        """
        Close an existing ticket.
        
        Args:
            ticket_id: The ID of the ticket to close
            closed_by: The Discord user ID of who closed the ticket
            
        Returns:
            bool: True if the ticket was closed, False otherwise
        """
        if ticket_id in self.tickets and not self.tickets[ticket_id]["closed"]:
            self.tickets[ticket_id]["closed"] = True
            self.tickets[ticket_id]["closed_at"] = datetime.now().isoformat()
            self.tickets[ticket_id]["closed_by"] = closed_by
            self._save_tickets()
            logger.info(f"Closed ticket {ticket_id} by user {closed_by}")
            return True
        return False

    def get_user_open_ticket(self, user_id: int) -> Optional[str]:
        """
        Get the ID of an open ticket for a user if one exists.
        
        Args:
            user_id: The Discord user ID to check
            
        Returns:
            Optional[str]: The ticket ID if found, None otherwise
        """
        for ticket_id, ticket in self.tickets.items():
            if ticket["user_id"] == user_id and not ticket["closed"]:
                return ticket_id
        return None

    def get_ticket_stats(self) -> Dict:
        """
        Get statistics about tickets.
        
        Returns:
            Dict: Statistics about tickets
        """
        total = len(self.tickets)
        open_tickets = sum(1 for t in self.tickets.values() if not t["closed"])
        closed_tickets = total - open_tickets
        
        return {
            "total": total,
            "open": open_tickets,
            "closed": closed_tickets
        }

    def get_user_tickets(self, user_id: int) -> List[Dict]:
        """
        Get all tickets for a specific user.
        
        Args:
            user_id: The Discord user ID to get tickets for
            
        Returns:
            List[Dict]: List of tickets for the user
        """
        return [
            {"ticket_id": tid, **tdata}
            for tid, tdata in self.tickets.items()
            if tdata["user_id"] == user_id
        ]
