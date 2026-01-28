from ollama import Client

# Connect to local Ollama Windows service
client = Client(host="http://localhost:11434")

def ollama_generate(prompt: str, model: str = "mistral") -> str:
    """
    Sends prompt to local Ollama model running on Windows.
    Returns generated text or None if Ollama isn't running.
    """
    try:
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print("⚠️ Ollama connection failed:", e)
        return None
