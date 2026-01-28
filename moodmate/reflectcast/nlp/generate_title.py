from google import genai
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_podcast_title(reflection: str, mood: str) -> str:
    prompt = (
        f"Generate a short, creative podcast title of 2 to 3 words "
        f"for a {mood} reflection: {reflection}. "
        f"Return only the title text."
    )

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash-8b",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print("Gemini failed:", e)
        return "Untitled Reflection"
