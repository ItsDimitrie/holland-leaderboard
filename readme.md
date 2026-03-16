# VPG Holland — Discord Leaderboard Bot

A Discord bot that fetches the MEE6 XP leaderboard and posts a live-updating embed in your server, refreshing every 60 seconds.

## Features

- Shows the top 25 members with rank, level, XP, and message count
- Medal emojis for the top 10 (🥇🥈🥉 for the podium, 4️⃣–🔟 for ranks 4–10)
- Visual dividers separating the podium, top 10, and the rest
- Server icon thumbnail pulled automatically from Discord
- Edits the same message on each refresh — no channel spam
- Clickable link to the full MEE6 leaderboard

## Setup

### 1. Clone and install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```
DISCORD_TOKEN=your_bot_token_here
CHANNEL_ID=the_channel_id_to_post_in
MEE6_SERVER_ID=your_discord_server_id
TOP=25
```

- **DISCORD_TOKEN** — from the [Discord Developer Portal](https://discord.com/developers/applications)
- **CHANNEL_ID** — right-click a channel in Discord → Copy Channel ID (needs Developer Mode on)
- **MEE6_SERVER_ID** — the numbers at the end of your MEE6 leaderboard URL
- **TOP** — how many members to show (default: 25)

### 3. Bot permissions

The bot needs these permissions in the channel:
- Read Messages
- Send Messages
- Embed Links

No privileged intents required.

### 4. Run locally

```bash
python leaderboard_bot.py
```

## Hosting on Railway

1. Push this repo to GitHub
2. Create a new project on [Railway](https://railway.app) and connect your repo
3. Add the environment variables from `.env` in the Railway dashboard under **Variables**
4. Railway will detect the `Procfile` and start the bot automatically as a worker
