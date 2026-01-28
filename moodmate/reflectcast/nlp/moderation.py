import re

# 🚨 HIGH-RISK / BLOCKED CONTENT
# Immediate intervention – do NOT store or generate
HARD_WORDS = [
    # Self-harm / suicide
    "kill myself", "suicide", "end my life", "die", "want to die",
    "hurt myself", "self harm", "cut myself",

    # Violence / threats
    "kill", "murder", "rape", "bomb", "shoot", "stab",
    "terrorist", "massacre",

    # Severe abuse
    "hang myself", "overdose", "jump off", "burn myself"
]

# ⚠️ SOFT / UNPLEASANT / FILTHY LANGUAGE
# Allowed, but triggers gentle warning & grounding tone
SOFT_WORDS = [
    # Swear words
    "fuck", "fucking", "fucked", "fucker",
    "shit", "shitty", "bullshit",
    "asshole", "bastard", "bitch", "damn",

    # Degrading / hateful self-talk
    "worthless", "useless", "hopeless", "pathetic",
    "i hate myself", "i'm broken", "i'm a failure",
    "no one cares", "i don't matter",

    # Anger / hostility
    "hate everyone", "i'm done with everything",
    "life is pointless", "nothing matters",

    # Sexual filth (non-graphic)
    "porn", "sex addict", "dirty thoughts"
]


def normalize(text: str) -> str:
    """Normalize text for safer matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def contains_word(text: str, word: str) -> bool:
    """Check word or phrase boundary-aware."""
    return re.search(rf"\b{re.escape(word)}\b", text) is not None


def check_content(text: str) -> str:
    """
    Returns:
        - 'hard'  → block & show support message
        - 'soft'  → allow but warn & soften tone
        - 'clean' → normal processing
    """
    text = normalize(text)

    for word in HARD_WORDS:
        if contains_word(text, word):
            return "hard"

    for word in SOFT_WORDS:
        if contains_word(text, word):
            return "soft"

    return "clean"
