# embedding_utils.py
import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"

def embed_text(text, model="nomic-embed-text"):
    response = requests.post(OLLAMA_EMBED_URL, json={
        "model": model,
        "prompt": text
    })
    response.raise_for_status()
    return response.json()["embedding"]


