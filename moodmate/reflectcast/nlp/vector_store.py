import os
import uuid
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

class LocalEmbeddingFunction:
    def __call__(self, input):
        if isinstance(input, str):
            input = [input]
        return model.encode(input).tolist()

    def name(self):
        return "local-sentence-transformer"

# Persistent Chroma client
chroma_client = chromadb.PersistentClient(
    path="./chroma_data",
    settings=Settings(allow_reset=True)
)

# ---------------------------
# Helper: get per-user collection
# ---------------------------
def get_user_collection(user_id):
    return chroma_client.get_or_create_collection(
        name=f"reflectcast_user_{user_id}",
        embedding_function=LocalEmbeddingFunction()
    )

# ---------------------------
# Text chunking
# ---------------------------
def chunk_text(text, max_tokens=450):
    sentences = text.split(". ")
    chunks = []
    current_chunk = []
    current_len = 0

    for sentence in sentences:
        tokens = len(sentence.split())
        if current_len + tokens <= max_tokens:
            current_chunk.append(sentence)
            current_len += tokens
        else:
            chunks.append(". ".join(current_chunk))
            current_chunk = [sentence]
            current_len = tokens

    if current_chunk:
        chunks.append(". ".join(current_chunk))

    return chunks

# ---------------------------
# Store reflection
# ---------------------------
def add_reflection(user_id, reflection_text, mood, outcome=None, theme=None, episode_script=None):
    collection = get_user_collection(user_id)
    chunks = chunk_text(reflection_text)
    today = datetime.now().strftime("%Y-%m-%d")

    for i, chunk in enumerate(chunks):
        try:
            collection.add(
                documents=[chunk],
                metadatas=[{
                    "mood": mood,
                    "date": today,
                    "theme": theme or "general",
                    "outcome": outcome or "unknown",
                    "episode_script": episode_script or "",
                    "chunk_index": i
                }],
                ids=[str(uuid.uuid4())]
            )
        except Exception as e:
            print(f"Error adding reflection chunk: {e}")

# ---------------------------
# Retrieve similar reflections (per user)
# ---------------------------
def get_similar_reflections(query_text, user_id, top_k=5):
    collection = get_user_collection(user_id)

    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
    except Exception as e:
        print(f"Error querying vector store: {e}")
        return []

    docs = []
    for i in range(len(results["documents"][0])):
        docs.append({
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i]
        })

    return docs
