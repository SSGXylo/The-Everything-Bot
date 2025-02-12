# Discord Multi-Purpose Bot

A feature-rich Discord bot with ticket system, moderation tools, security features, mini-games, welcome system, and leveling.

## Features

### 🎫 Ticket System
- Create and manage support tickets
- Private channels for each ticket
- Ticket tracking and logging
- Support team integration

### 🛡️ Moderation Commands
- `/kick` - Kick members with logging
- `/ban` - Ban members with optional message deletion
- `/mute` - Timeout members for specified duration
- `/unmute` - Remove timeout from members
- `/warn` - Issue warnings to members

### 🔒 Security Features
- Anti-spam protection
- Anti-raid measures
- Server nuke prevention
- Automatic moderation actions
- Detailed security logging

### 🎮 Mini-Games
1. **Rock Paper Scissors** (`/rps`)
   - Play against the bot
   - Interactive button interface
   
2. **Number Guessing** (`/guess`)
   - Guess numbers with hints
   - Customizable range
   - Multiple attempts

3. **Trivia** (`/trivia`)
   - Multiple-choice questions
   - Various topics
   - Score tracking

### 👋 Welcome System
- Customizable welcome messages
- Auto-role assignment
- Welcome message testing
- Supports member mentions and server variables

### ⭐ Leveling System
- Experience (XP) tracking
- Level-up notifications
- Role rewards
- Server leaderboard
- Customizable XP rates
- Anti-spam measures

## Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/DiscordBot.git
cd DiscordBot
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create a `.env` file in the root directory:
```env
DISCORD_TOKEN=your_bot_token_here
ENCRYPTION_KEY=your_secure_encryption_key  # Optional
GUILD_ID=your_guild_id  # Optional
```

4. **Run the Bot**
```bash
python run.py
```

## Required Permissions

The bot requires the following permissions:
- Manage Channels
- Manage Roles
- Kick Members
- Ban Members
- Moderate Members
- View Channels
- Send Messages
- Manage Messages
- Read Message History
- Add Reactions

## Bot Commands

### Ticket Commands
- `/setup` - Set up the ticket system
- `/stats` - View ticket statistics
- `/mytickets` - View your ticket history

### Moderation Commands
- `/kick @user [reason]` - Kick a member
- `/ban @user [reason] [delete_days]` - Ban a member
- `/mute @user [duration] [reason]` - Mute a member
- `/unmute @user` - Unmute a member
- `/warn @user [reason]` - Warn a member

### Game Commands
- `/rps` - Play Rock Paper Scissors
- `/guess [max_number]` - Play Number Guessing
- `/trivia` - Play Trivia

### Welcome Commands
- `/welcome_setup` - Configure welcome messages and auto-role
- `/welcome_test` - Test the welcome message

### Leveling Commands
- `/rank [member]` - View your or another member's rank
- `/leaderboard` - Display the XP leaderboard
- `/levelconfig` - Configure the leveling system
- `/addrole_reward` - Add role rewards for levels

### Security Commands
- `/anti_nuke_settings` - View security settings

## Project Structure
```
DiscordBot/
├── src/
│   ├── __init__.py
│   ├── bot.py
│   ├── config.py
│   ├── cogs/
│   │   ├── tickets.py
│   │   ├── moderation.py
│   │   ├── security.py
│   │   ├── games.py
│   │   ├── welcome.py
│   │   └── leveling.py
│   ├── utils/
│   │   ├── logger.py
│   │   ├── security.py
│   │   └── encryption.py
│   └── views/
│       └── ticket_views.py
├── data/
├── logs/
├── requirements.txt
├── run.py
└── README.md
```

## Security Features

- Encrypted data storage
- Rate limiting
- Role hierarchy checks
- Permission validation
- Anti-spam measures
- Raid protection
- Detailed logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.
