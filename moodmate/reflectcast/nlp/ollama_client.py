from ollama import Client

client = Client(host="http://localhost:11434")

def ollama_generate(prompt: str, model: str = "gemma3:4b") -> str:
    try:
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        print("⚠️ Ollama connection failed:", e)
        return None
