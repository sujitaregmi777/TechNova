# generate_title.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_podcast_title(reflection: str, mood: str) -> str:
    """Generate a short, catchy podcast title using GPT-4o-mini."""
    prompt = f"Generate a short, creative podcast title (max 3 words) for a {mood} reflection: {reflection}"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=15,
        temperature=0.7,
    )
    return resp.choices[0].message.content.strip()

# Example
if __name__ == "__main__":
    print(generate_podcast_title("I felt grateful for small joys today.", "grateful"))
