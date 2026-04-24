from sentence_transformers import SentenceTransformer
from typing import List

_MODEL = None

def _load_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL

def embed_text(text: str) -> List[float]:
    """Embed a single string and return a vector (list of floats)."""
    model = _load_model()
    vec = model.encode([text], show_progress_bar=False)[0]
    return vec.tolist()

def embed_texts(texts: List[str]) -> List[List[float]]:
    model = _load_model()
    vecs = model.encode(texts, show_progress_bar=False)
    return [v.tolist() for v in vecs]
