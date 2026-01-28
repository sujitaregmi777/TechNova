HARD_BLOCK = [
    "kill yourself",
    "you should die",
    "i will kill",
]

SOFT_BLOCK = [
    "stupid",
    "idiot",
    "your fault",
]

def check_content(text):
    text = text.lower()

    if any(word in text for word in HARD_BLOCK):
        return "hard"

    if any(word in text for word in SOFT_BLOCK):
        return "soft"

    return "ok"
