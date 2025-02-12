#!/usr/bin/env python3
"""
Entry point for The Everything Bot.
Handles bot initialization and startup.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Import bot from src
from src.bot import main

if __name__ == '__main__':
    main()
