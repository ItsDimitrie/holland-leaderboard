# leaderboard_bot.py
# Discord bot that fetches the MEE6 leaderboard and displays the top members
# as an embed, refreshing every 180 seconds by editing the same message.
#
# Requirements:
#   pip install discord.py aiohttp python-dotenv

import os, asyncio, aiohttp, discord
from discord.ext import tasks
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID    = int(os.getenv("CHANNEL_ID", "0"))
SERVER_ID     = os.getenv("MEE6_SERVER_ID", "792410559948914738")
TOP           = int(os.getenv("TOP", "25"))   # how many members to show

MEE6_API = f"https://mee6.xyz/api/plugins/levels/leaderboard/{SERVER_ID}?limit=100&page=0"

MEDALS = {
    1: "🥇", 2: "🥈", 3: "🥉",
    4: "4️⃣", 5: "5️⃣", 6: "6️⃣",
    7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟",
}

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

# Holds the message we'll keep editing so we don't flood the channel.
leaderboard_message: discord.Message | None = None


def build_embed(players: list[dict], server_name: str, guild: dict) -> discord.Embed:
    shown = players[:TOP]
    count = len(shown)

    embed = discord.Embed(
        title=f"🏆 {server_name} — XP Leaderboard",
        color=discord.Color.orange(),
        timestamp=datetime.now(timezone.utc),
    )

    # Server icon as thumbnail
    guild_id   = guild.get("id")
    guild_icon = guild.get("icon")
    if guild_id and guild_icon:
        embed.set_thumbnail(url=f"https://cdn.discordapp.com/icons/{guild_id}/{guild_icon}.png")

    if not shown:
        embed.description = "No data available."
        return embed

    segments = ["╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌"]
    for i, player in enumerate(shown, start=1):
        medal = MEDALS.get(i, f"`{i}.`")
        name  = player.get("username", "unknown")
        level = player.get("level", 0)
        xp    = player.get("xp", 0)
        msgs  = player.get("message_count", 0)
        segments.append(f"{medal} **{name}** — Level {level} · {xp:,} XP · {msgs:,} posts")
        # Visual dividers after the podium and after the top 10
        if i in (3, 10) and i < count:
            segments.append("╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌")

    embed.description = "\n\u200b\n".join(segments)

    # Divider between the list and the footer fields
    embed.add_field(name="╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌", value="\u200b", inline=False)

    # Clickable MEE6 link as a field so it renders as a hyperlink
    embed.add_field(
        name="📊 Meer details?",
        value=f"[Bekijk de volledige leaderboard op MEE6](https://mee6.xyz/en/leaderboard/{SERVER_ID})",
        inline=False,
    )

    now = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    embed.set_footer(text=f"🕐 Geüpdatet om {now}  •  🏅 Blijf actief en win prijzen!  •  © VPG Holland 2026")
    return embed


@client.event
async def on_ready():
    print(f"Logged in as {client.user} ({client.user.id})")
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"ERROR: channel {CHANNEL_ID} not found — check CHANNEL_ID in .env")
        return

    # Send an initial placeholder so we have a message to edit.
    global leaderboard_message
    placeholder = discord.Embed(
        title="🏆 VPG Holland Leaderboard",
        description="Loading…",
        color=discord.Color.orange(),
    )
    leaderboard_message = await channel.send(embed=placeholder)
    refresh_leaderboard.start()


@tasks.loop(seconds=180)
async def refresh_leaderboard():
    global leaderboard_message
    if leaderboard_message is None:
        return

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(MEE6_API, headers={"Accept": "application/json"}) as resp:
                if resp.status != 200:
                    print(f"MEE6 API returned HTTP {resp.status}")
                    return
                data = await resp.json()

        players     = data.get("players", [])
        guild       = data.get("guild", {})
        server_name = guild.get("name", "Server")
        embed       = build_embed(players, server_name, guild)
        await leaderboard_message.edit(embed=embed)

    except asyncio.TimeoutError:
        print("MEE6 API timed out")
    except Exception as e:
        print(f"Error refreshing leaderboard: {e}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        raise SystemExit("DISCORD_TOKEN not set — add it to your .env file")
    if CHANNEL_ID <= 0:
        raise SystemExit("CHANNEL_ID not set or invalid — add it to your .env file")
    client.run(DISCORD_TOKEN)
