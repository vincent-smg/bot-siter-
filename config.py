import os

class Config:
    """Central configuration, loaded from environment variables."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-to-a-random-secret")
    
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///anko_uguisu.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PREFERRED_URL_SCHEME = "https"

    DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
    DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI", "https://bot-siter.onrender.com/callback")
    
    DISCORD_API_BASE_URL = "https://discord.com/api"
    DISCORD_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
    DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
    DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
    DISCORD_BOT_INVITE_URL = os.environ.get("DISCORD_BOT_INVITE_URL", "")
    USERNAME_CHECK_INTERVAL = int(os.environ.get("USERNAME_CHECK_INTERVAL", "600"))
    STATUS_API_KEY = os.environ.get("STATUS_API_KEY", "change-me-bot-status-key")
    SUPPORT_SERVER_URL = os.environ.get("SUPPORT_SERVER_URL", "https://discord.gg/your-invite-code")
    PREMIUM_URL = os.environ.get("PREMIUM_URL", "https://ko-fi.com/your-page")

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_ENABLED = os.environ.get("RATELIMIT_ENABLED", "true").lower() != "false"
