import json
import os
import secrets
from datetime import datetime, timedelta

from dotenv import load_dotenv


load_dotenv()

import requests
from flask import (
    Flask,
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix

from config import Config
from data.commands import COMMAND_CATEGORIES, PREFIX
from data.dashboard_settings import DASHBOARD_SECTIONS
from data.premium import PREMIUM_PERKS, PREMIUM_TIERS
from data.updates import UPDATES
from models import GuildSettings, User, db
from config import Config # Import the Config class from your file

app = Flask(__name__)
app.config.from_object(Config) # Load all settings from the Config class

# Now apply the middleware
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(BASE_DIR, "data", "bot_status.json")

DEFAULT_STATUS = {
    "online": False,
    "latency_ms": None,
    "guild_count": 0,
    "user_count": 0,
    "shard_count": 1,
    "started_at": None,
    "last_updated": None,
    "guilds": [],
}


# Discord permission bitflags we care about for the dashboard.
PERM_ADMINISTRATOR = 0x8
PERM_MANAGE_GUILD = 0x20


def guild_permission_level(permissions):
    """
    Given the 'permissions' bitfield Discord returns for a guild in
    /users/@me/guilds, return "administrator", "manage_guild", or None.
    """
    try:
        perms = int(permissions)
    except (TypeError, ValueError):
        return None

    if perms & PERM_ADMINISTRATOR:
        return "administrator"
    if perms & PERM_MANAGE_GUILD:
        return "manage_guild"
    return None


def guild_icon_url(guild, size=64):
    """Jinja filter: build a CDN URL for a guild's icon, or None."""
    icon = (guild or {}).get("icon")
    guild_id = (guild or {}).get("id")
    if not icon or not guild_id:
        return None
    ext = "gif" if icon.startswith("a_") else "png"
    return f"https://cdn.discordapp.com/icons/{guild_id}/{icon}.{ext}?size={size}"


def create_app():
    app = Flask(__name__)

    # ------------------------------------------------------------------
    # Trust Render's proxy headers.
    # ------------------------------------------------------------------
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ------------------------------------------------------------------
    # Rate limiting
    # ------------------------------------------------------------------
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per hour"],
        storage_uri=app.config["RATELIMIT_STORAGE_URI"],
        enabled=app.config["RATELIMIT_ENABLED"],
    )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def read_status():
        if not os.path.exists(STATUS_FILE):
            return dict(DEFAULT_STATUS)
        try:
            with open(STATUS_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return dict(DEFAULT_STATUS)

        merged = dict(DEFAULT_STATUS)
        merged.update(data)

        # If the bot hasn't reported in over 2 minutes, treat it as offline
        if merged.get("last_updated"):
            try:
                last = datetime.fromisoformat(merged["last_updated"])
                if datetime.utcnow() - last > timedelta(minutes=2):
                    merged["online"] = False
            except ValueError:
                pass
        return merged

    def write_status(data):
        os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
        with open(STATUS_FILE, "w") as f:
            json.dump(data, f)

    def exchange_code_for_token(code):
        data = {
            "client_id": app.config["DISCORD_CLIENT_ID"],
            "client_secret": app.config["DISCORD_CLIENT_SECRET"],
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": app.config["DISCORD_REDIRECT_URI"],
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(
            app.config["DISCORD_TOKEN_URL"], data=data, headers=headers, timeout=10
        )
        resp.raise_for_status()
        return resp.json()

    def refresh_access_token(refresh_token):
        data = {
            "client_id": app.config["DISCORD_CLIENT_ID"],
            "client_secret": app.config["DISCORD_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(
            app.config["DISCORD_TOKEN_URL"], data=data, headers=headers, timeout=10
        )
        resp.raise_for_status()
        return resp.json()

    def fetch_discord_user(access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(
            f"{app.config['DISCORD_API_BASE_URL']}/users/@me",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def fetch_discord_guilds(access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        resp = requests.get(
            f"{app.config['DISCORD_API_BASE_URL']}/users/@me/guilds",
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def get_valid_access_token(user):
        if user.token_expires_at and datetime.utcnow() >= user.token_expires_at:
            if not user.refresh_token:
                return None
            try:
                token_data = refresh_access_token(user.refresh_token)
            except requests.RequestException:
                return None

            user.access_token = token_data["access_token"]
            user.refresh_token = token_data.get(
                "refresh_token", user.refresh_token
            )
            user.token_expires_at = datetime.utcnow() + timedelta(
                seconds=token_data.get("expires_in", 0)
            )
            db.session.commit()

        return user.access_token

    def upsert_user(discord_user, token_data):
        discord_id = discord_user["id"]
        user = User.query.get(discord_id)
        expires_at = datetime.utcnow() + timedelta(
            seconds=token_data.get("expires_in", 0)
        )

        if user is None:
            user = User(discord_id=discord_id)
            db.session.add(user)

        user.username = discord_user.get("username", user.username)
        user.global_name = discord_user.get("global_name")
        user.avatar_hash = discord_user.get("avatar")
        user.access_token = token_data.get("access_token", user.access_token)
        user.refresh_token = token_data.get("refresh_token", user.refresh_token)
        user.token_expires_at = expires_at
        user.last_login_at = datetime.utcnow()
        user.last_checked_at = datetime.utcnow()

        db.session.commit()
        return user

    # ------------------------------------------------------------------
    # Before request hooks
    # ------------------------------------------------------------------
    @app.before_request
    def load_logged_in_user():
        g.user = None
        discord_id = session.get("discord_id")
        if not discord_id:
            return

        user = User.query.get(discord_id)
        if user is None:
            session.clear()
            return

        g.user = user

        interval = app.config["USERNAME_CHECK_INTERVAL"]
        last_checked = user.last_checked_at or datetime.min
        if datetime.utcnow() - last_checked < timedelta(seconds=interval):
            return

        access_token = user.access_token
        try:
            if user.token_expires_at and datetime.utcnow() >= user.token_expires_at:
                if not user.refresh_token:
                    raise RuntimeError("no refresh token")
                token_data = refresh_access_token(user.refresh_token)
                access_token = token_data["access_token"]
                user.access_token = access_token
                user.refresh_token = token_data.get(
                    "refresh_token", user.refresh_token
                )
                user.token_expires_at = datetime.utcnow() + timedelta(
                    seconds=token_data.get("expires_in", 0)
                )
                db.session.commit()

            discord_user = fetch_discord_user(access_token)
        except Exception:
            return

        new_username = discord_user.get("username")
        new_global_name = discord_user.get("global_name")

        if new_username != user.username or new_global_name != user.global_name:
            user.username = new_username
            user.global_name = new_global_name
            user.avatar_hash = discord_user.get("avatar")
            db.session.commit()

            session.clear()
            g.user = None
            flash(
                "We noticed your Discord username changed. "
                "Please sign in again to refresh your account."
            )
        else:
            user.last_checked_at = datetime.utcnow()
            db.session.commit()

    @app.context_processor
    def inject_globals():
        return {
            "current_user": g.get("user"),
            "invite_url": app.config["DISCORD_BOT_INVITE_URL"],
            "support_server_url": app.config["SUPPORT_SERVER_URL"],
            "premium_url": app.config["PREMIUM_URL"],
            "bot_name": "Anko Uguisu",
        }

    app.jinja_env.filters["guild_icon_url"] = guild_icon_url

    # ------------------------------------------------------------------
    # Auth routes
    # ------------------------------------------------------------------
    @app.route("/login")
    @limiter.limit("10 per minute")
    def login():
        if g.user:
            return redirect(url_for("index"))

        state = secrets.token_urlsafe(16)
        session["oauth_state"] = state

        params = {
            "client_id": app.config["DISCORD_CLIENT_ID"],
            "redirect_uri": app.config["DISCORD_REDIRECT_URI"],
            "response_type": "code",
            "scope": "identify guilds",
            "state": state,
            "prompt": "consent",
        }
        query = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items())
        return redirect(f"{app.config['DISCORD_AUTHORIZE_URL']}?{query}")

    @app.route("/callback")
    @limiter.limit("10 per minute")
    def callback():
        error = request.args.get("error")
        if error:
            flash("Discord sign-in was cancelled.")
            return redirect(url_for("index"))

        state = request.args.get("state")
        if not state or state != session.pop("oauth_state", None):
            abort(400, description="Invalid OAuth state.")

        code = request.args.get("code")
        if not code:
            flash("Missing authorization code from Discord.")
            return redirect(url_for("index"))

        try:
            token_data = exchange_code_for_token(code)
            discord_user = fetch_discord_user(token_data["access_token"])
        except requests.RequestException as e:
            # Prints the raw Discord HTTP status response directly into Render logs
            print(f"--- [DEBUG] DISCORD API EXCHANGE ERROR: {e} ---", flush=True)
            if hasattr(e, 'response') and e.response is not None:
                print(f"--- [DEBUG] RESPONSE BODY: {e.response.text} ---", flush=True)
                
            flash("Could not reach Discord. Please try again.")
            return redirect(url_for("index"))

        user = upsert_user(discord_user, token_data)
        session["discord_id"] = user.discord_id
        flash(f"Signed in as {user.display_name()}.")
        return redirect(url_for("index"))

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been signed out.")
        return redirect(url_for("index"))

    # ------------------------------------------------------------------
    # Page routes
    # ------------------------------------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/commands")
    def commands_page():
        return render_template(
            "commands.html",
            categories=COMMAND_CATEGORIES,
            prefix=PREFIX,
        )

    @app.route("/premium")
    def premium_page():
        return render_template(
            "premium.html",
            perks=PREMIUM_PERKS,
            tiers=PREMIUM_TIERS,
        )

    @app.route("/status")
    def status_page():
        return render_template("status.html", status=read_status())

    @app.route("/updates")
    def updates_page():
        return render_template("updates.html", updates=UPDATES)

    @app.route("/policy")
    def policy_page():
        return render_template("policy.html")

    @app.route("/terms")
    def terms_page():
        return render_template("terms.html")

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------
    @app.route("/dashboard")
    def dashboard():
        if not g.user:
            flash("Please sign in with Discord to view your dashboard.")
            return redirect(url_for("login"))

        access_token = get_valid_access_token(g.user)
        managed_guilds = []

        if not access_token:
            flash("Your Discord session expired. Please sign in again.")
            return redirect(url_for("login"))

        try:
            user_guilds = fetch_discord_guilds(access_token)
        except requests.RequestException:
            user_guilds = []
            flash(
                "Couldn't reach Discord to load your servers. "
                "Please try again in a moment."
            )

        bot_guild_ids = {str(gd.get("id")) for gd in read_status().get("guilds", [])}

        for guild in user_guilds:
            level = guild_permission_level(guild.get("permissions"))
            if level and str(guild.get("id")) in bot_guild_ids:
                managed_guilds.append(
                    {
                        "id": guild["id"],
                        "name": guild["name"],
                        "icon": guild.get("icon"),
                        "permission_level": level,
                    }
                )

        managed_guilds.sort(key=lambda gd: gd["name"].lower())
        return render_template("dashboard.html", guilds=managed_guilds)

    @app.route("/dashboard/<guild_id>", methods=["GET", "POST"])
    def dashboard_guild(guild_id):
        if not g.user:
            flash("Please sign in with Discord to view your dashboard.")
            return redirect(url_for("login"))

        access_token = get_valid_access_token(g.user)
        if not access_token:
            flash("Your Discord session expired. Please sign in again.")
            return redirect(url_for("login"))

        try:
            user_guilds = fetch_discord_guilds(access_token)
        except requests.RequestException:
            flash("Couldn't reach Discord to verify your permissions.")
            return redirect(url_for("dashboard"))

        guild_info = next(
            (gd for gd in user_guilds if str(gd.get("id")) == str(guild_id)), None
        )
        permission_level = (
            guild_permission_level(guild_info.get("permissions"))
            if guild_info
            else None
        )

        if not guild_info or not permission_level:
            abort(403)

        bot_guild_ids = {str(gd.get("id")) for gd in read_status().get("guilds", [])}
        if str(guild_id) not in bot_guild_ids:
            abort(404)

        settings = GuildSettings.query.get(guild_id)
        if settings is None:
            settings = GuildSettings(guild_id=guild_id, data={})

        visible_sections = [
            section
            for section in DASHBOARD_SECTIONS
            if permission_level == "administrator"
            or section["required_permission"] == "manage_guild"
        ]

        if request.method == "POST":
            section_id = request.form.get("section")
            section = next(
                (s for s in visible_sections if s["id"] == section_id), None
            )
            if section is None:
                abort(400)

            data = dict(settings.data or {})
            for field in section["fields"]:
                key = field["key"]
                if field["type"] == "toggle":
                    data[key] = request.form.get(key) == "on"
                elif field["type"] == "list":
                    raw = request.form.get(key, "")
                    data[key] = [
                        line.strip() for line in raw.splitlines() if line.strip()
                    ]
                else:
                    data[key] = request.form.get(key, "").strip()

            settings.data = data
            settings.guild_name = guild_info.get("name")
            settings.guild_icon = guild_info.get("icon")
            db.session.add(settings)
            db.session.commit()

            flash(f"Saved {section['label']} settings.")
            return redirect(f"{url_for('dashboard_guild', guild_id=guild_id)}#{section_id}")

        return render_template(
            "dashboard_guild.html",
            guild=guild_info,
            permission_level=permission_level,
            sections=visible_sections,
            settings=settings.data or {},
        )

    # ------------------------------------------------------------------
    # Status API
    # ------------------------------------------------------------------
    @app.route("/api/status", methods=["GET"])
    @limiter.limit("30 per minute")
    def api_status_get():
        return jsonify(read_status())

    @app.route("/api/status", methods=["POST"])
    @limiter.limit("20 per minute")
    def api_status_post():
        key = request.headers.get("X-Status-Key")
        if key != app.config["STATUS_API_KEY"]:
            abort(401)

        payload = request.get_json(silent=True) or {}
        status = read_status()
        for field in (
            "latency_ms",
            "guild_count",
            "user_count",
            "shard_count",
            "started_at",
            "guilds",
        ):
            if field in payload:
                status[field] = payload[field]

        status["online"] = True
        status["last_updated"] = datetime.utcnow().isoformat()
        write_status(status)
        return jsonify({"ok": True})

    # ------------------------------------------------------------------
    # Guild config API
    # ------------------------------------------------------------------
    @app.route("/api/guild-config/<guild_id>", methods=["GET"])
    @limiter.limit("60 per minute")
    def api_guild_config(guild_id):
        key = request.headers.get("X-Status-Key")
        if key != app.config["STATUS_API_KEY"]:
            abort(401)

        settings = GuildSettings.query.get(guild_id)
        return jsonify(settings.data if settings else {})

    @app.route("/api/guild-configs", methods=["GET"])
    @limiter.limit("30 per minute")
    def api_guild_configs():
        key = request.headers.get("X-Status-Key")
        if key != app.config["STATUS_API_KEY"]:
            abort(401)

        all_settings = GuildSettings.query.all()
        return jsonify({s.guild_id: (s.data or {}) for s in all_settings})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
