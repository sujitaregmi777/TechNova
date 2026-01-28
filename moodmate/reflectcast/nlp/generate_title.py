

from moodmate.reflectcast.nlp.ollama_client import ollama_generate

def generate_podcast_title(reflection: str, emotion: str) -> str:
    prompt = (
        "You are a gentle journaling assistant.\n"
        "Create one short, meaningful title (max 2 words) that summarizes this reflection.\n"
        "Return ONLY the title text.\n\n"
        f"Reflection:\n{reflection}"
    )

    title = ollama_generate(prompt)
    if title:
        print(" Generated Title:", title)
        return title.strip()

    # Fallback title
    return f"A Moment of {emotion.capitalize()}"
 