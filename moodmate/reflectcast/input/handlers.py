import os
from datetime import datetime

BASE_UPLOAD_DIR = "uploads"
JOURNAL_DIR = os.path.join(BASE_UPLOAD_DIR, "journals")
CHAT_DIR = os.path.join(BASE_UPLOAD_DIR, "chats")


def ensure_dirs():
    """Ensure required upload directories exist."""
    os.makedirs(JOURNAL_DIR, exist_ok=True)
    os.makedirs(CHAT_DIR, exist_ok=True)


def generate_filename(prefix: str, extension="txt"):
    """Generate unique timestamp-based filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def save_reflection(text: str):
    """
    Save user journal reflection into uploads/journals/
    Returns saved filepath.
    """
    ensure_dirs()
    filename = generate_filename("reflection")
    filepath = os.path.join(JOURNAL_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text.strip())

    return filepath


def save_chat(chat_text: str):
    """
    Save AI chat conversation into uploads/chats/
    Returns saved filepath.
    """
    ensure_dirs()
    filename = generate_filename("chat")
    filepath = os.path.join(CHAT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(chat_text.strip())

    return filepath


def list_reflections():
    """Return list of saved reflection filenames sorted newest first."""
    ensure_dirs()
    files = os.listdir(JOURNAL_DIR)
    return sorted(files, reverse=True)


def list_chats():
    """Return list of saved chat filenames sorted newest first."""
    ensure_dirs()
    files = os.listdir(CHAT_DIR)
    return sorted(files, reverse=True)


def load_file(folder: str, filename: str):
    """
    Load text from a saved file.
    folder must be 'journals' or 'chats'.
    """
    base = JOURNAL_DIR if folder == "journals" else CHAT_DIR
    filepath = os.path.join(base, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError("File not found")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def process_input(text: str, input_type="reflection"):
    """
    Main entry point.
    Behaves like your old save_reflection(),
    but supports both reflections and chats.
    """
    if input_type == "reflection":
        return save_reflection(text)

    elif input_type == "chat":
        return save_chat(text)

    else:
        raise ValueError("input_type must be 'reflection' or 'chat'")
