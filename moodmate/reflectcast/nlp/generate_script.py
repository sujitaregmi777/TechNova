import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI
from reflectcast.nlp.vector_store import add_reflection, get_similar_reflections

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY environment variable not set")

client = OpenAI(api_key=OPENAI_API_KEY)

def clean_text(text):
    """Remove weird quotes and formatting artifacts."""
    return (text.replace("’", "'")
                .replace("‘", "'")
                .replace("“", '"')
                .replace("”", '"')
                .replace("\u200b", '')
                .strip())

def build_prompt(reflection: str, emotion: str, memory_context: str) -> str:
    return (
        f"The user shared this reflection today about feeling {emotion}:\n"
        f"\"\"\"\n{reflection}\n\"\"\"\n\n"
        f"Here are some past reflections to personalize the response:\n{memory_context}\n\n"
        "Now, write a poetic, emotionally comforting bedtime podcast script (~50 words). "
        "The tone should be gentle, calming, and empathetic. It should help the user feel seen, supported, and at peace. "
        "Begin with a warm, gentle greeting to invite the listener in. The tone should be comforting, kind, and emotionally supportive throughout."
        "End with a peaceful, soothing message, either wishing them good night (if appropriate to the time) or offering a reassuring reminder like 'I'm here whenever you need me."
        " The goal is to leave the listener feeling safe, calm, and cared for."
        " Do not include section labels or any formatting tags."
    )

def create_script(reflection: str, emotion: str,user_id: str) -> str:
    try:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        # Save user reflection to vector store
        add_reflection(
            user_id=user_id,
            reflection_text=reflection,
            mood=emotion,
            outcome=None,
            theme=None,
            episode_script=None
        )

        # Get similar past reflections for memory context
        similar_docs = get_similar_reflections(reflection, user_id=user_id)
        memory_contexts = []
        for doc in similar_docs:
            meta = doc.get("metadata", {})
            text = doc.get("document", "")
            if text != reflection:
                memory_contexts.append(
                    f"This is what the user felt on {meta.get('date', 'unknown')} because of this: \"{text[:120]}...\""
                )
        memory_context = "\n".join(memory_contexts) if memory_contexts else "No specific memory found, but the user has felt deeply before."

        # Build prompt
        prompt = build_prompt(reflection, emotion, memory_context)

        # Generate script using OpenAI chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a compassionate bedtime podcast writer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=450,
            temperature=0.7,
        )

        return clean_text(response.choices[0].message.content.strip())

    except Exception as e:
        print(f"Error generating script: {e}")
        return clean_text(
            "Hello there.\n\n"
            "Take a deep breath and settle into this moment.\n\n"
            "Life can be overwhelming, but you’re doing your best — and that’s enough.\n\n"
            "Let go of any tension, and allow yourself to relax.\n\n"
            "Tonight is your time to rest, to heal, and simply be.\n\n"
            "Remember, you are not alone. Wishing you a calm and restful night."
        )
