"""
Logging utility for the Discord Ticket Bot.
"""
import logging
from datetime import datetime
from pathlib import Path
from ..config import LOGS_DIR

def setup_logger(name: str) -> logging.Logger:
    """
    Set up a logger with the specified name.
    
    Args:
        name: The name of the logger
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create formatters and handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    current_date = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_DIR / f"{current_date}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Create main logger instance
logger = setup_logger('ticket_bot')
