import datetime
from moodmate.reflectcast.nlp.moderation import check_content
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
        "You are Moodmate — a calm reflective companion that helps users slow down and observe their thoughts. "
        "You do NOT provide therapy, medical advice, or emotional validation. "
        "You offer gentle reflection and grounding only.\n\n"

        f"Today's journal reflection (emotion detected: {emotion}):\n"
        f"\"\"\"\n{reflection}\n\"\"\"\n\n"

        f"Past reflections for personalization:\n{memory_context}\n\n"

        "Write a short bedtime-style audio script (~60 words). "
        "Tone: gentle, calming, empathetic, grounded. "
        "Begin with a warm welcoming greeting. "
        "Offer one soft reflective insight or observation. "
        "Avoid giving advice or solutions. "
        "End with a peaceful closing line that makes the listener feel safe and settled. "
        "Return only the script text. No titles, no labels, no formatting."
    )


def create_script(reflection: str, emotion: str, user_id: str) -> str:
    try:
        moderation_result = check_content(reflection)
        if moderation_result == "hard":
            return (
                "I’m really glad you shared this. "
                "It sounds like you’re facing something very heavy right now. "
                "Moodmate can’t handle crisis situations, but you deserve real human support. "
                "If you're in immediate danger, please contact local emergency services or a trusted person nearby."
            )
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

        if moderation_result == "soft":
            prompt = (
                "The user used strong or harsh language. "
                "Respond with extra softness and grounding tone.\n\n"
            ) + prompt

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
