"""
Example: reporting live stats from the Anko Uguisu bot to the website.

Run this periodically from within the bot process (e.g. in a discord.py
@tasks.loop every 60 seconds) to keep the /status page up to date.

    from tasks import loop
    @loop(seconds=60)
    async def report_status():
        report_status(bot)

This file is just a reference - copy what you need into the bot's codebase.
"""

import os
import time

import requests

WEBSITE_URL = os.environ.get("ANKO_WEBSITE_URL", "http://localhost:5000")
STATUS_API_KEY = os.environ.get("STATUS_API_KEY", "change-me-bot-status-key")

BOT_STARTED_AT = time.time()


def report_status(bot):
    """
    bot: a discord.py Client/Bot instance.
    """
    payload = {
        "latency_ms": round(bot.latency * 1000),
        "guild_count": len(bot.guilds),
        "user_count": sum(g.member_count or 0 for g in bot.guilds),
        "shard_count": bot.shard_count or 1,
        "started_at": BOT_STARTED_AT,
    }

    try:
        requests.post(
            f"{WEBSITE_URL}/api/status",
            json=payload,
            headers={"X-Status-Key": STATUS_API_KEY},
            timeout=5,
        )
    except requests.RequestException:
        # Don't let a website hiccup take down the bot
        pass
