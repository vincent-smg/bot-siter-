from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """
    A logged-in Discord user.

    discord_id is the permanent Discord snowflake ID and is used as the
    primary key, since usernames can change. The 'username' column always
    holds the most recently-seen Discord username so it survives username
    changes (it gets refreshed on every login / periodic check).
    """

    __tablename__ = "users"

    discord_id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    global_name = db.Column(db.String(64), nullable=True)
    avatar_hash = db.Column(db.String(64), nullable=True)

    access_token = db.Column(db.String(256), nullable=True)
    refresh_token = db.Column(db.String(256), nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_checked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def avatar_url(self):
        if self.avatar_hash:
            ext = "gif" if self.avatar_hash.startswith("a_") else "png"
            return (
                f"https://cdn.discordapp.com/avatars/"
                f"{self.discord_id}/{self.avatar_hash}.{ext}?size=128"
            )
        # Default Discord embed avatar
        return "https://cdn.discordapp.com/embed/avatars/0.png"

    def display_name(self):
        return self.global_name or self.username


class GuildSettings(db.Model):
    """
    Per-server settings configured through the website dashboard.

    Everything configurable lives in the 'data' JSON blob, keyed by the
    field 'key' values defined in data/dashboard_settings.py. This keeps
    adding new dashboard settings simple - no migrations needed, just add
    a new field to a section and read/write that key from the bot.

    The bot fetches this via:
        GET /api/guild-config/<guild_id>      (single server)
        GET /api/guild-configs                (all servers at once)
    both protected by the X-Status-Key header (STATUS_API_KEY).
    """

    __tablename__ = "guild_settings"

    guild_id = db.Column(db.String(32), primary_key=True)
    guild_name = db.Column(db.String(100), nullable=True)
    guild_icon = db.Column(db.String(64), nullable=True)

    data = db.Column(db.JSON, nullable=False, default=dict)

    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def get(self, key, default=None):
        return (self.data or {}).get(key, default)
