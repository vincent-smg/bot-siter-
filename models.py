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


class PremiumSubscription(db.Model):
    """
    A premium purchase made on the website, tied to a Discord account.

    This is the single source of truth the bot polls (via GET
    /api/premium-sync) to know who currently has premium. The flow is:

        1. User clicks "Get Premium" on the website -> a row is created
           here with status="pending" while they pay.
        2. Payment succeeds (mock provider for now, real TBC/BOG later)
           -> status flips to "active" and expires_at is set ~30 days out.
        3. The bot asks /api/premium-sync every 30s "who's active right
           now?" and mirrors the answer into its own premium_users set -
           no manual /setpremium needed anymore.
        4. When expires_at passes, is_active() naturally returns False,
           so the user drops out of the next sync automatically.
    """

    __tablename__ = "premium_subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(32), db.ForeignKey("users.discord_id"), nullable=False, index=True)
    tier_id = db.Column(db.String(32), nullable=False)  # "premium" or "premium_plus"

    # pending -> active -> (cancelled | expired)
    status = db.Column(db.String(16), nullable=False, default="pending")

    provider = db.Column(db.String(16), nullable=False, default="mock")  # "mock" or "tbc"
    external_payment_id = db.Column(db.String(128), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    activated_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    def is_active(self):
        if self.status != "active":
            return False
        if self.expires_at and datetime.utcnow() >= self.expires_at:
            return False
        return True