import os
import pickle
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORE_DIR = os.path.join(BASE_DIR, "tfidf_store")
os.makedirs(STORE_DIR, exist_ok=True)

# ---------------------------
# Helpers to load/save per user store
# ---------------------------

def _get_user_store_path(user_id):
    return os.path.join(STORE_DIR, f"user_{user_id}.pkl")

def _load_user_store(user_id):
    path = _get_user_store_path(user_id)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return {
        "documents": [],
        "metadatas": []
    }

def _save_user_store(user_id, data):
    path = _get_user_store_path(user_id)
    with open(path, "wb") as f:
        pickle.dump(data, f)

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
    store = _load_user_store(user_id)
    chunks = chunk_text(reflection_text)
    today = datetime.now().strftime("%Y-%m-%d")

    for i, chunk in enumerate(chunks):
        store["documents"].append(chunk)
        store["metadatas"].append({
            "mood": mood,
            "date": today,
            "theme": theme or "general",
            "outcome": outcome or "unknown",
            "episode_script": episode_script or "",
            "chunk_index": i
        })

    _save_user_store(user_id, store)

# ---------------------------
# Retrieve similar reflections
# ---------------------------

def get_similar_reflections(query_text, user_id, top_k=5):
    store = _load_user_store(user_id)

    documents = store["documents"]
    metadatas = store["metadatas"]

    if not documents:
        return []

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents + [query_text])

    cosine_sim = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    )[0]

    top_indices = cosine_sim.argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        results.append({
            "document": documents[idx],
            "metadata": metadatas[idx]
        })

    return results
