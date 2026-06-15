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
from data.premium import PREMIUM_PERKS, PREMIUM_TIERS
from data.updates import UPDATES
from models import User, db

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
}


def create_app():
    app = Flask(__name__)

    # ------------------------------------------------------------------
    # Trust Render's proxy headers.
    #
    # Render (and the Cloudflare layer in front of it) terminates TLS and
    # forwards requests to your app over plain HTTP, adding
    # X-Forwarded-For / X-Forwarded-Proto / X-Forwarded-Host headers.
    # Without this, Flask thinks every request is plain HTTP from
    # Render's internal IP, which breaks:
    #   - secure cookies (SESSION_COOKIE_SECURE)
    #   - https:// OAuth redirect URIs
    #   - rate limiting / logging by real client IP
    #
    # x_for=1 / x_proto=1 / x_host=1 means "trust exactly one layer of
    # proxy" for each of those headers, which matches Render's setup.
    # ------------------------------------------------------------------
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    app.config.from_object(Config)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    # ------------------------------------------------------------------
    # Rate limiting
    #
    # Render's own DDoS protection handles large-scale floods, but
    # per-route rate limiting protects specific sensitive endpoints
    # (login/OAuth, the bot status webhook) from abuse, brute-forcing,
    # or accidental loops. Limits are keyed on the real client IP thanks
    # to ProxyFix above.
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
    # Before/after request: load current user + periodically verify
    # their Discord username hasn't changed. If it has, log them out so
    # the new username is picked up next time they sign in.
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

        # Time to re-check the user's Discord username
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
            # If Discord can't be reached or the token is invalid, just
            # skip the check this time rather than breaking the request.
            return

        new_username = discord_user.get("username")
        new_global_name = discord_user.get("global_name")

        if new_username != user.username or new_global_name != user.global_name:
            # Username changed since last login - save the new value but
            # sign the user out so they reauthenticate with fresh data.
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
            "scope": "identify",
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
        except requests.RequestException:
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
    # Status API - the bot process pushes live stats here, the status
    # page polls it for live numbers.
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
        ):
            if field in payload:
                status[field] = payload[field]

        status["online"] = True
        status["last_updated"] = datetime.utcnow().isoformat()
        write_status(status)
        return jsonify({"ok": True})

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
