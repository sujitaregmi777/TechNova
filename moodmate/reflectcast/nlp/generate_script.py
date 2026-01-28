import datetime
from moodmate.reflectcast.nlp.ollama_client import ollama_generate
from moodmate.reflectcast.nlp.vector_store import add_reflection, get_similar_reflections


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
        f"You are a mate that reflect and provide insights to ground you.\n\n"
        f"The user shared this reflection today about feeling {emotion}:\n"
        f"\"\"\"\n{reflection}\n\"\"\"\n\n"
        f"Here are some past reflections to personalize the response:\n{memory_context}\n\n"
        "Write a poetic, emotionally comforting bedtime podcast script (~60 words). "
        "The tone should be gentle, calming, and empathetic. "
        "Begin with a warm, gentle greeting to invite the listener in. "
        "End with a peaceful, soothing closing line that makes the listener feel safe and cared for. "
        "Return only the script text. No labels or formatting."
    )


def create_script(reflection: str, emotion: str, user_id: str) -> str:
    try:
        # Store reflection in vector memory
        add_reflection(
            user_id=user_id,
            reflection_text=reflection,
            mood=emotion,
            outcome=None,
            theme=None,
            episode_script=None
        )
        print(" Stored reflection in vector store.")
        print(" Retrieving similar reflections...")
        # Retrieve similar past reflections
        similar_docs = get_similar_reflections(reflection, user_id=user_id)
        memory_contexts = []

        for doc in similar_docs:
            meta = doc.get("metadata", {})
            text = doc.get("document", "")
            if text and text != reflection:
                memory_contexts.append(
                    f"On {meta.get('date', 'a past day')}, the user once reflected: \"{text[:120]}...\""
                )

        memory_context = "\n".join(memory_contexts) if memory_contexts else \
            "The user has felt deeply before, even if no specific memory is found."

        # Build prompt
        prompt = build_prompt(reflection, emotion, memory_context)

        # ---- Generate using Ollama ----
        print(" Generating script....")
        script = ollama_generate(prompt)

        if script:
            print(" Generated Script using Ollama:", script)
            return clean_text(script)

        raise Exception("Empty Ollama response")

    except Exception as e:
        print("⚠️ Script generator fallback:", e)
        return clean_text(
            "Hello gentle soul. Take a slow breath. "
            "You’ve done enough for today. "
            "Let your body soften and your thoughts quiet. "
            "You are safe, you are cared for, and you may rest now."
        )
