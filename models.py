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
