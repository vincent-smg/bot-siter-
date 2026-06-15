"""
Premium feature & tier definitions for Anko Uguisu.

Edit this file to change what shows up on the /premium page - the perk
list, the pricing tiers, and the FAQ. Nothing here is wired up to real
payments; PREMIUM_URL (in config.py / your .env) controls where every
"Get Premium" button points (Ko-fi, Patreon, a Discord premium role
purchase link, etc).
"""

PREMIUM_PERKS = [
    {
        "title": "Custom rank card backgrounds",
        "description": "Upload your own image with /setbg and Anko will use it as your rank card background instead of the default night sky.",
        "icon": "image",
    },
    {
        "title": "Exclusive shop decos",
        "description": "Unlock premium-only frames and decorations in the /shop that aren't available to free members.",
        "icon": "sparkle",
    },
    {
        "title": "Boosted coin & XP gains",
        "description": "Earn extra coins from /daily and a small XP multiplier from chatting, so you climb the leaderboard faster.",
        "icon": "coin",
    },
    
    {
        "title": "Premium badge",
        "description": "A gold badge next to your name on /rank and the /leaderboard so everyone knows you're supporting the bot.",
        "icon": "badge",
    },
    {
        "title": "Early access to new features",
        "description": "Premium members get to try new commands and systems before they're rolled out to everyone else.",
        "icon": "rocket",
    },
]

PREMIUM_TIERS = [
    {
        "id": "premium",
        "name": "Premium",
        "price": "$0.99",
        "period": "/ month",
        "tagline": "A small boost to say thanks.",
        "featured": False,
        "features": [
            "Custom rank card backgrounds (/setbg)",
            "custom rank color customization",
            "Boosted daily coin rewards",
           
            
            
        ],
    },
    {
        "id": "premium_plus",
        "name": "Premium+",
        "price": "$2.99",
        "period": "/ month",
        "tagline": "The full Anko experience.",
        "featured": True,
        "features": [
            "Everything in Premium",
            "custom rank background(/setbg)",
            "custom rank color customization(/changecolor)",
            "XP & coin boost while chatting",
            "Early access to new features",
        ],
    },
]
