"""
Dashboard settings sections for Anko Uguisu.

Each entry in DASHBOARD_SECTIONS becomes one card on
/dashboard/<guild_id>. To add a new setting:

1. Add a field to an existing section's "fields" list, OR add a whole
   new section dict to DASHBOARD_SECTIONS.
2. That's it on the website side - app.py reads this list generically,
   so new fields are automatically rendered, saved, and exposed to the
   bot via /api/guild-config/<guild_id> without any other code changes.
3. On the bot side, read the new key (it'll be a key in the JSON dict
   returned by /api/guild-config/<guild_id>) and use it wherever that
   setting applies (e.g. cogs/welcome.py reading "welcome_channel_id").

Field types:
  - "toggle":   on/off switch. Stored as a bool (True/False).
  - "text":     single-line text input. Stored as a string.
  - "textarea": multi-line text input. Stored as a string.
  - "list":     one item per line in a textarea. Stored as a list of
                 strings (great for word filters, role IDs, etc).

required_permission controls who can see/edit the section:
  - "manage_guild"  -> anyone with the "Manage Server" permission
  - "administrator" -> only server Administrators
"""

DASHBOARD_SECTIONS = [
    {
        "id": "welcome",
        "label": "Welcome Messages",
        "description": "Configure the message Anko sends when a new member joins.",
        "required_permission": "manage_guild",
        "fields": [
            {
                "key": "welcome_enabled",
                "label": "Enable welcome messages",
                "type": "toggle",
            },
            {
                "key": "welcome_channel_id",
                "label": "Welcome channel ID",
                "type": "text",
                "placeholder": "e.g. 1440011473496834252",
                "help": "Right-click the channel in Discord and choose 'Copy Channel ID'.",
            },
            {
                "key": "welcome_message",
                "label": "Welcome message",
                "type": "textarea",
                "placeholder": "welcome to the gang!",
                "help": "Use {user} to mention the member and {server} for the server name.",
            },
            {
                "key": "welcome_color",
                "label": "Welcome embed color",
                "type": "text",
                "placeholder": "9B59B6",
                "help": "Hex color for the welcome message (e.g., 9B59B6 or #9B59B6).",
            },
            {
                "key": "welcome_gif_url",
                "label": "Welcome GIF URL",
                "type": "text",
                "placeholder": "https://...",
                "help": "Optional background GIF link.",
            },
        ],
    },
    {
        "id": "goodbye",
        "label": "Goodbye Messages",
        "description": "Configure the message Anko sends when a member leaves.",
        "required_permission": "manage_guild",
        "fields": [
            {
                "key": "goodbye_enabled",
                "label": "Enable goodbye messages",
                "type": "toggle",
            },
            {
                "key": "goodbye_channel_id",
                "label": "Goodbye channel ID",
                "type": "text",
                "placeholder": "e.g. 1440011473496834252",
            },
            {
                "key": "goodbye_message",
                "label": "Goodbye message",
                "type": "textarea",
                "placeholder": "has left the gang.",
            },
            {
                "key": "goodbye_color",
                "label": "Goodbye embed color",
                "type": "text",
                "placeholder": "FF0000",
                "help": "Hex color for the goodbye message (e.g., FF0000 or #FF0000).",
            },
            {
                "key": "goodbye_gif_url",
                "label": "Goodbye GIF URL",
                "type": "text",
                "placeholder": "https://...",
                "help": "Optional background GIF link.",
            },
        ],
    },
    {
        "id": "word_filter",
        "label": "Word Filter",
        "description": "Messages containing these words are automatically removed and may trigger timeout escalation.",
        "required_permission": "manage_guild",
        "fields": [
            {
                "key": "word_filter_enabled",
                "label": "Enable word filter",
                "type": "toggle",
            },
            {
                "key": "word_filter_words",
                "label": "Filtered words",
                "type": "list",
                "placeholder": "one word per line",
                "help": "One word or phrase per line. Matching is case-insensitive.",
            },
        ],
    },
    {
        "id": "witbot",
        "label": "Witbot (AI Chat)",
        "description": "Controls for Anko's AI chat persona in this server.",
        "required_permission": "administrator",
        "fields": [
            {
                "key": "witbot_enabled",
                "label": "Enable Witbot in this server",
                "type": "toggle",
            },
            {
                "key": "witbot_channel_id",
                "label": "Witbot channel ID",
                "type": "text",
                "placeholder": "e.g. 1440011473496834252",
            },
            {
                "key": "witbot_persona",
                "label": "Witbot persona / description",
                "type": "textarea",
                "placeholder": "Describe how Witbot should act in this server...",
            },
        ],
    },
]
