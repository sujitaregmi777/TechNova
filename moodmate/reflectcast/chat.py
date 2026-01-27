import os
from openai import OpenAI

# Load key from .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY environment variable not set")

# ✅ New OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def chat_with_openai(conversation):
    """
    conversation: list of dicts
    [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=conversation,
            temperature=0.7
        )

        # ✅ IMPORTANT: new SDK uses dot notation
        return response.choices[0].message.content

    except Exception as e:
        print("OpenAI API error:", e)
        return "I’m here with you 🌙 Tell me a little more."
