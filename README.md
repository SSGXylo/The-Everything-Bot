# Discord Ticket Bot

A Discord bot that implements a ticket system for support requests.

## Features

- Create support tickets with a button click
- Automatically creates private channels for each ticket
- Close tickets when resolved
- Prevents users from creating multiple open tickets
- Administrators can set up the ticket system in any channel

## Setup Instructions

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure the bot:
   - Create a new Discord application and bot at https://discord.com/developers/applications
   - Copy your bot token
   - Replace "your_bot_token_here" in the `.env` file with your actual bot token

3. Invite the bot to your server with the following permissions:
   - Manage Channels
   - View Channels
   - Send Messages
   - Manage Messages
   - Read Message History
   - Add Reactions
   - Use Slash Commands

4. Run the bot:
```bash
python bot.py
```

5. Use the `/setup` command in your server to create the ticket system

## Usage

1. Users can create tickets by clicking the "Create Ticket" button
2. A private channel will be created for the ticket
3. Support staff can communicate with the user in the ticket channel
4. Use the "Close Ticket" button to close and delete the ticket when resolved

## Note

Make sure the bot has the necessary permissions in your server to:
- Create channels and categories
- Manage channel permissions
- Send messages and embeds
- Use slash commands
