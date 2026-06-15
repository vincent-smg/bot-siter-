"""
Prefix command definitions for Anko Uguisu.

Edit this list to add, remove, or change commands shown on the /commands page.
Each entry becomes one card. 'usage' is the exact text copied to the
clipboard when the card is clicked.
"""

PREFIX = "."

COMMAND_CATEGORIES = [
    {
        "id": "leveling",
        "label": "Leveling & Economy",
        "commands": [
            {
                "name": "level",
                "usage": "/level [@user]",
                "description": "Shows your (or someone else's) rank card with level, XP and progress.",
            },
             {
                "name": "setlevelchannel",
                "usage": "/setlevelchannel [channel]",
                "description": "Sets the channel where level up cards will be sent.",
            },
            {
                "name": "leaderboard",
                "usage": "/leaderboard",
                "description": "Displays the server's top members by level and XP.",
            },
            {
                "name": "balance",
                "usage": "/balance [@user]",
                "description": "Checks how many coins you or another member currently have.",
            },
            {
                "name": "daily",
                "usage": "daily",
                "description": "Claims your daily coin reward.",
            },
            {
                "name": "coinflip <amount> <heads or tails>",
                "usage": "coinflip <amount>",
                "description": "Bets coins on a heads-or-tails flip with an animated result.",
            },
            {
                "name": "give",
                "usage": "give @user <amount>",
                "description": "Sends coins to another member, who can accept or decline.",
            },
            {
                "name": "choosedeco",
                "usage": "choosedeco",
                "description": "Sets a chosen deco as your profile decoration (premium).",
                
            },
            {
                "name": "removedeco",
                "usage": "removedeco",
                "description": "removes your current deco (if premium it will be set to premium deco)",
                
            },
            {
                "name": "shop",
                "usage": "shop",
                "description": "Opens the deco shop to browse rank card decorations.",
            },
            {
                "name": "inventory",
                "usage": "inventory",
                "description": "shows you your inventory",
            },
            {
                "name": "sell",
                "usage": "sell",
                "description": "sell an item from your inventory",
            },

            {
                "name": "setbg",
                "usage": "/setbg",
                "description": "Sets a custom rank card background (premium).",
                "premium": True,
            },
            {
                "name": "changecolor",
                "usage": "/changecolor",
                "description": "Sets a custom rank card color accent (premium).",
                "premium": True,
            },
           
        ],
    },
    {
        "id": "anime",
        "label": "Anime Interactions",
        "commands": [
            {
                "name": "kiss",
                "usage": "/kiss @user",
                "description": "Sends an anime kiss GIF to the mentioned member.",
            },
            {
                "name": "hug",
                "usage": "/hug @user",
                "description": "Sends a warm anime hug GIF to the mentioned member.",
            },
            {
                "name": "pat",
                "usage": "/pat @user",
                "description": "Gives the mentioned member a friendly head pat.",
            },
            {
                "name": "bite",
                "usage": "/bite @user",
                "description": "Sends a playful anime bite GIF to the mentioned member.",
            },
            {
                "name": "baka",
                "usage": "/baka @user",
                "description": "Calls the mentioned member a baka with a fitting reaction GIF.",
            },
            {
                "name": "askmommyai",
                "usage": "/askmommyai <message>",
                "description": "Chats with Anko's alternate AI persona.",
            },
            {
                "name": "setwitbotchannel",
                "usage": "/setwitbotchannel <channel> <description>",
                "description": "Set the AI channel and the system description/personality rules.",
            },
            {
                "name": "witbottalk",
                "usage": "/witbottalk",
                "description": "Turn the AI response system on or off for this server.",
            },
        ],
    },
    {
        "id": "moderation",
        "label": "Moderation",
        "commands": [
            {
                "name": "kick",
                "usage": "kick @user [reason]",
                "description": "Kicks a member from the server.",
            },
            {
                "name": "ban",
                "usage": "ban @user [reason]",
                "description": "Bans a member from the server.",
            },
            {
                "name": "timeout",
                "usage": "timeout @user <duration> [reason]",
                "description": "Times out a member for the given duration.",
            },
            {
                "name": "warn",
                "usage": "warn @user [reason]",
                "description": "Issues a warning to a member.",
            },
            {
                "name": "purge",
                "usage": "purge <amount>",
                "description": "Deletes the given number of recent messages.",
            },
            {
                "name": "addwordfilter",
                "usage": "/addwordfilter <word>",
                "description": "Adds a word to the server's word filter.",
            },
            {
                "name": "removewordfilter",
                "usage": "/removewordfilter <word>",
                "description": "Removes a word from the server's word filter.",
            },
        ],
    },
    {
        "id": "utility",
        "label": "Utility & Fun",
        "commands": [
            {
                "name": "marry",
                "usage": "/marry <@user>",
                "description": "Marks you as AFK and notifies anyone who pings you.",
            },
            {
                "name": "myring",
                "usage": "/myring ",
                "description": "shows you the ring you have",
            },
             {
                "name": "divorce",
                "usage": "/divorce <@user>",
                "description": "divorce your partner",
            },
            {
                "name": "forcedivorce",
                "usage": "/forcedivorce <@user>",
                "description": "pay to forcefully divorce your partner",
            },
            {
                "name": "partner",
                "usage": "/partner <@user>",
                "description": "see your or other persons partner",
            },
            {
                "name": "afk",
                "usage": "afk [reason]",
                "description": "Marks you as AFK and notifies anyone who pings you.",
            },
            {
                "name": "buy",
                "usage": "buy <tier>",
                "description": "buy a ring",
            },
            {
                "name": "buybox",
                "usage": "buy box <amount>",
                "description": "buy a deco box",
            },
            {
                "name": "openbox",
                "usage": "openbox <amount>",
                "description": "open a deco box",
            },
            {
                "name": "impersonate",
                "usage": "impersonate <@user> <text>",
                "description": "makes someones fake profile send a message ",
            },
            {
                "name": "snipe",
                "usage": "snipe <number from newest to oldest> ",
                "description": "Shows a deleted message ",
            },
             {
                "name": "8ball",
                "usage": "8ball <question>",
                "description": "Sends a random answer to a question.",
            },

             {
                "name": "achievement",
                "usage": "/achievement ",
                "description": "sends a custom legacy minecraft achievement",
            },
             {
                "name": "randomcat",
                "usage": "/randomcat",
                "description": "sends a random cat image",
            },
             {
                "name": "shutup",
                "usage": "shutup",
                "description": "deletes every message of person that is in shutup",
            },
            
            {
                "name": "warn <@user> <warningtext>",
                "usage": "warn",
                "description": "sends a dm to the person with warning message",
            },
            {
                "name": "dih <user>",
                "usage": "dih",
                "description": "random pp size",
            },
             {
                "name": "warnings",
                "usage": "warnings",
                "description": "shows list of warned people",
            },
            {
                "name": "robloxavatar",
                "usage": "/robloxavatar <username>",
                "description": "Looks up a Roblox profile.",
            },
            {
                "name": "avatar",
                "usage": "avatar <username>",
                "description": "sends a persons discord profile.",
            },
            {
                "name": "roll",
                "usage": "diceroll",
                "description": "rolls the dice",
            },
            {
                "name": "poll",
                "usage": "poll",
                "description": "sends a yes and no question poll",
            },
            {
                "name": "mcprofile",
                "usage": "/mcprofile <name>",
                "description": "Checks the status of a Minecraft server.",
            },
            {
                "name": "setwelcome",
                "usage": "/setwelcome <channel> [message] [color] [gif_url]",
                "description": "Set the welcome channel, custom message, hex color, and optional background GIF.",
            },
            {
                "name": "setgoodbye",
                "usage": "/setgoodbye <channel> [message] [color] [gif_url]",
                "description": "Set the goodbye channel, custom message, hex color, and optional background GIF.",
            },
            {
                "name": "setdirtychannel",
                "usage": "/setdirtychannel <channel>",
                "description": "Set the channel where dirty jokes will be sent and automatically mark it as NSFW.",
            },
             {
                "name": "dirtyjoke",
                "usage": "/dirtyjoke",
                "description": "sends a dirty joke (only in dirty channel)",
            },
             {
                "name": "how",
                "usage": "how <description word> <@user>",
                "description": "measure how much (description word) (@user) is",
            },
            
            {
                "name": "dadjoke",
                "usage": "/dadjoke",
                "description": "Sends a random dad joke.",
            },
             {
                "name": "darkjoke",
                "usage": "/darkjoke",
                "description": "Sends a random dark joke.",
            },
           
        ],
    },
]
