"""
Example: reporting live stats from the Anko Uguisu bot to the website,
and pulling per-server dashboard settings back down.

Run report_status() periodically from within the bot process (e.g. in a
discord.py @tasks.loop every 60 seconds) to keep the /status page and the
dashboard's server list up to date.

    from discord.ext import tasks

    @tasks.loop(seconds=60)
    async def report_status():
        report_status(bot)

    @tasks.loop(seconds=120)
    async def sync_guild_configs():
        configs = fetch_all_guild_configs()
        # apply configs to your cogs, e.g.:
        # word_filter_cog.update_filters(configs)

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

    Sends live stats AND the list of guilds Anko is currently in. The
    guild list is what powers the "is Anko in this server?" check on the
    /dashboard page - a server only shows up there if it's in this list
    AND the logged-in user has Manage Server / Administrator there.
    """
    payload = {
        "latency_ms": round(bot.latency * 1000),
        "guild_count": len(bot.guilds),
        "user_count": sum(g.member_count or 0 for g in bot.guilds),
        "shard_count": bot.shard_count or 1,
        "started_at": BOT_STARTED_AT,
        "guilds": [
            {
                "id": str(guild.id),
                "name": guild.name,
                "icon": guild.icon.key if guild.icon else None,
            }
            for guild in bot.guilds
        ],
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


def fetch_guild_config(guild_id):
    """
    Fetch dashboard-configured settings for one server, e.g.:

        {
          "welcome_enabled": true,
          "welcome_channel_id": "123456789012345678",
          "welcome_message": "Welcome to the server, {user}!",
          "word_filter_enabled": true,
          "word_filter_words": ["badword1", "badword2"],
          ...
        }

    Returns {} if nothing has been configured yet for this server.
    Field names match the "key" values in data/dashboard_settings.py.
    """
    try:
        resp = requests.get(
            f"{WEBSITE_URL}/api/guild-config/{guild_id}",
            headers={"X-Status-Key": STATUS_API_KEY},
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return {}


def fetch_all_guild_configs():
    """
    Fetch dashboard settings for every server at once:

        {
          "123456789012345678": { "welcome_enabled": true, ... },
          "987654321098765432": { ... },
        }

    More efficient than calling fetch_guild_config() per-guild on a
    timer - use this for periodic syncs.
    """
    try:
        resp = requests.get(
            f"{WEBSITE_URL}/api/guild-configs",
            headers={"X-Status-Key": STATUS_API_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return {}
