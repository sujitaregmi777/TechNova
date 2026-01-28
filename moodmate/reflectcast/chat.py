import os
from openai import OpenAI


def get_openai_client():
    """Get OpenAI client, checking for API key."""
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY environment variable not set")
    return OpenAI(api_key=OPENAI_API_KEY)


def chat_with_openai(conversation):
    """
    conversation: list of dicts
    [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
    """
    try:
        client = get_openai_client()
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
