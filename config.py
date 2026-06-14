import os


class Config:
    """
    Central configuration, loaded from environment variables.

    Copy .env.example to .env and fill in your own values before running
    the app. Never commit your real .env file.
    """

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-to-a-random-secret")

    # Database (SQLite by default - swap for Postgres/MySQL in production)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///anko_uguisu.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Discord OAuth2 application credentials
    # Create an application at https://discord.com/developers/applications
    DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
    DISCORD_REDIRECT_URI = os.environ.get(
        "DISCORD_REDIRECT_URI", "http://localhost:5000/callback"
    )

    # Discord OAuth2 endpoints
    DISCORD_API_BASE_URL = "https://discord.com/api"
    DISCORD_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
    DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"

    # Invite link for the "Invite" button (top right of the navbar).
    # Generate this from the OAuth2 URL Generator in the Discord developer
    # portal with the "bot" + "applications.commands" scopes.
    DISCORD_BOT_INVITE_URL = os.environ.get(
        "DISCORD_BOT_INVITE_URL",
        "https://discord.com/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=8&scope=bot%20applications.commands",
    )

    # How often (in seconds) a logged-in user's Discord username is
    # re-checked. If it has changed since they logged in, they are
    # signed out and asked to log in again so the new username is saved.
    USERNAME_CHECK_INTERVAL = int(os.environ.get("USERNAME_CHECK_INTERVAL", "600"))

    # Shared secret the bot process uses to push live stats to
    # POST /api/status. Set this to a long random string and configure
    # the same value on the bot side.
    STATUS_API_KEY = os.environ.get("STATUS_API_KEY", "change-me-bot-status-key")

    # Support server invite link, used as a fallback contact link in
    # the footer and terms/policy pages.
    SUPPORT_SERVER_URL = os.environ.get(
        "SUPPORT_SERVER_URL", "https://discord.gg/your-invite-code"
    )

    # Where the "Get Premium" buttons send people - e.g. a Ko-fi,
    # Patreon, or Discord premium role purchase link. Falls back to the
    # support server so the button always goes somewhere useful.
    PREMIUM_URL = os.environ.get("PREMIUM_URL", "https://ko-fi.com/your-page")
