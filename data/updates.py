"""
Update log entries for Anko Uguisu.

Newest entries should be added to the TOP of this list — the /updates
page renders them in the order given here.
"""

UPDATES = [
    {
        "date": "2026-06-10",
        "tag": "Feature",
        "title": "Rank card decorations",
        "summary": (
            "Added a shop-based decoration system for rank cards. "
            "Buy frames and badges with coins and equip them with a!equipdeco."
        ),
    },
    {
        "date": "2026-05-28",
        "tag": "Improvement",
        "title": "Coinflip animations",
        "summary": (
            "a!coinflip now plays an animated embed sequence before "
            "revealing the result, and supports the new coin emojis."
        ),
    },
    {
        "date": "2026-05-19",
        "tag": "Feature",
        "title": "Give & accept coins",
        "summary": (
            "a!give now sends an Accept / Decline prompt to the recipient "
            "before any coins change hands."
        ),
    },
    {
        "date": "2026-05-02",
        "tag": "Rewrite",
        "title": "Leveling system overhaul",
        "summary": (
            "Rank cards and level-up cards were rebuilt with a new "
            "purple and teal night-sky theme. XP and coins now sync "
            "globally across every server Anko is in."
        ),
    },
    {
        "date": "2026-04-14",
        "tag": "Fix",
        "title": "Slash command timeouts resolved",
        "summary": (
            "Fixed an issue where commands could fail with a Discord "
            "interaction timeout under heavy load."
        ),
    },
    {
        "date": "2026-03-30",
        "tag": "Feature",
        "title": "Premium custom backgrounds",
        "summary": (
            "Premium members can now set a custom rank card background "
            "with a!setbg."
        ),
    },
]
