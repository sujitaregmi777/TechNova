import os
import datetime
import random
from dotenv import load_dotenv

from moodmate.reflectcast.nlp.vector_store import add_reflection, get_similar_reflections

# Try Gemini if available
try:
    from google import genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_AVAILABLE and GEMINI_KEY:
    client = genai.Client(api_key=GEMINI_KEY)
else:
    client = None


OPENING_LINES = [
    "Hello, gentle soul.",
    "Welcome back, dear friend.",
    "Take a slow breath with me.",
    "Settle into this quiet moment."
]

CLOSING_LINES = [
    "You are safe. Rest well.",
    "I’m here whenever you need me.",
    "Let the day drift away peacefully.",
    "You are cared for. Good night."
]


def clean_text(text):
    return text.strip()


def build_local_script(reflection, emotion, memory_context):
    """Offline poetic generator using reflection + memory"""

    opening = random.choice(OPENING_LINES)
    closing = random.choice(CLOSING_LINES)

    memory_line = ""
    if memory_context:
        memory_line = "I remember you’ve felt similar moments before. "

    return (
        f"{opening} "
        f"Tonight you shared feeling {emotion}. "
        f"{memory_line}"
        f"Your words matter: '{reflection[:80]}...'. "
        f"Let yourself soften. "
        f"{closing}"
    )


def create_script(reflection: str, emotion: str, user_id: str) -> str:
    try:
        # Save to vector DB
        add_reflection(
            user_id=user_id,
            reflection_text=reflection,
            mood=emotion,
            outcome=None,
            theme=None,
            episode_script=None
        )

        # Memory retrieval
        similar_docs = get_similar_reflections(reflection, user_id=user_id)
        memory_contexts = []

        for doc in similar_docs:
            text = doc.get("document", "")
            if text != reflection:
                memory_contexts.append(text)

        memory_context = "\n".join(memory_contexts)

        # --- Try Gemini if available ---
        if client:
            try:
                prompt = (
                    f"The user shared this reflection about feeling {emotion}:\n"
                    f"{reflection}\n\n"
                    f"Past reflections:\n{memory_context}\n\n"
                    "Write a gentle, comforting bedtime podcast script (~60 words)."
                )

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt
                )

                script = response.text.strip()
                if script:
                    return clean_text(script)

            except Exception:
                print("⚠️ Gemini unavailable → using offline script generator")

        # --- Always safe offline fallback ---
        return clean_text(build_local_script(reflection, emotion, memory_context))

    except Exception as e:
        print("⚠️ Script system fallback triggered:", e)
        return clean_text(build_local_script(reflection, emotion, ""))


# Test
if __name__ == "__main__":
    print(create_script(
        "I felt overwhelmed but proud I finished my work.",
        "motivated",
        "test_user"
    ))
