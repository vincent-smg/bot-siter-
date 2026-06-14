# Anko Uguisu — Website

A Flask website for the Anko Uguisu Discord bot: a landing page with
"Sign in with Discord", a commands directory, a live status page, an
updates/changelog page, and privacy policy / terms of service pages.

## Pages & endpoints

| Page | Route | Notes |
| --- | --- | --- |
| Home / sign in | `/` | Hero, sign-in CTA, invite button |
| Commands | `/commands` | Click-to-copy command cards, grouped by category |
| Status | `/status` | Live bot stats, auto-refreshes every 15s |
| Updates | `/updates` | Changelog cards |
| Privacy Policy | `/policy` | |
| Terms of Service | `/terms` | |
| Discord login | `/login`, `/callback`, `/logout` | OAuth2 flow |
| Status API | `/api/status` (GET/POST) | Bot pushes stats with `POST`, page polls with `GET` |

## 1. Set up a Discord application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and open (or create) your bot's application.
2. Under **OAuth2 → General**, copy the **Client ID** and **Client Secret**.
3. Under **OAuth2 → Redirects**, add: `http://localhost:5000/callback` (and your production URL later, e.g. `https://yourdomain.com/callback`).
4. Under **OAuth2 → URL Generator**, select scopes `bot` and `applications.commands`, pick the permissions your bot needs, and copy the generated URL — this is your `DISCORD_BOT_INVITE_URL`.

## 2. Configure environment variables

```bash
cp .env.example .env
```

Then fill in `.env`:

- `SECRET_KEY` — random string (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DISCORD_CLIENT_ID` / `DISCORD_CLIENT_SECRET` — from step 1
- `DISCORD_REDIRECT_URI` — must exactly match a redirect registered in step 1
- `DISCORD_BOT_INVITE_URL` — from step 1
- `STATUS_API_KEY` — random string; the bot uses this to push live stats
- `SUPPORT_SERVER_URL` — your community/support Discord invite

## 3. Install & run

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The site runs at `http://localhost:5000`. The SQLite database
(`anko_uguisu.db`) is created automatically on first run.

## 4. How sign-in works

- Clicking **Sign in with Discord** sends the user through Discord's
  OAuth2 flow with the `identify` scope (username, ID, avatar only — no
  email or server access).
- On callback, the user's Discord ID, username, and avatar are saved (or
  updated) in the `users` table.
- While a user is signed in, the site periodically (every
  `USERNAME_CHECK_INTERVAL` seconds, default 10 minutes) re-checks their
  Discord username. If it has changed, the new username is saved and the
  user is signed out so the change takes effect cleanly on their next
  login.

## 5. Editing content

- **Commands page**: edit `data/commands.py`. Each entry becomes a
  click-to-copy card; `usage` is what gets copied.
- **Updates page**: edit `data/updates.py`. Newest entries go at the top
  of the list. `tag` controls the card's color (`Feature`, `Fix`,
  `Improvement`, `Rewrite`, etc. — anything works, `Feature` and `Fix`
  get special colors).
- **Policy / Terms**: edit `templates/policy.html` and
  `templates/terms.html` directly.

## 6. Reporting live status from the bot

The `/status` page reads from `data/bot_status.json`, which your bot
process should update periodically via:

```
POST /api/status
Headers: X-Status-Key: <STATUS_API_KEY>
Body (JSON): {
  "latency_ms": 42,
  "guild_count": 12,
  "user_count": 3400,
  "shard_count": 1,
  "started_at": 1718000000
}
```

See `status_reporter_example.py` for a ready-to-adapt snippet using
discord.py — call it on a loop (e.g. every 60 seconds) from the bot. If
the bot hasn't reported in over 2 minutes, the status page automatically
shows "offline".

## 7. Project structure

```
anko-uguisu-site/
├── app.py                  # Flask app, routes, OAuth, status API
├── config.py               # Environment-based configuration
├── models.py                # SQLAlchemy User model
├── data/
│   ├── commands.py          # Commands shown on /commands
│   ├── updates.py            # Changelog entries shown on /updates
│   └── bot_status.json       # Written by /api/status (created at runtime)
├── templates/                # Jinja2 templates
├── static/
│   ├── css/style.css
│   ├── js/main.js
│   └── img/anko-logo.webp
├── status_reporter_example.py
├── requirements.txt
└── .env.example
```
