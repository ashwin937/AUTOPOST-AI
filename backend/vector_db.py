import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from embeddings import embed_text, embed_texts

load_dotenv()

CHROMA_PATH = os.path.join(os.getcwd(), "./chroma_data")

_client = None
_collection = None

def init_db():
    """Initialize persistent ChromaDB client and the 'posts' collection. Seed if empty."""
    global _client, _collection
    if _client is None:
        os.makedirs(CHROMA_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
    # create or get collection
    try:
        _collection = _client.get_collection("posts")
    except Exception:
        _collection = _client.create_collection(name="posts")

    # Seed if empty
    if _collection.count() == 0:
        _seed_samples()

def _now_iso():
    return datetime.utcnow().isoformat()

def _seed_samples():
    samples = [
        {
            "id": str(uuid.uuid4()),
            "document": "Launching our new product today! Check out the features and let us know what you think.",
            "metadata": {
                "platform": "twitter",
                "status": "published",
                "tone": "professional",
                "topic": "product launch",
                "scheduled_at": "",
                "created_at": _now_iso(),
                "engagement": 120
            }
        },
        {
            "id": str(uuid.uuid4()),
            "document": "Quick tips to boost your LinkedIn profile — 5 actionable steps.",
            "metadata": {
                "platform": "linkedin",
                "status": "published",
                "tone": "professional",
                "topic": "linkedin tips",
                "scheduled_at": "",
                "created_at": _now_iso(),
                "engagement": 230
            }
        },
        {
            "id": str(uuid.uuid4()),
            "document": "Behind the scenes on how we make our coffee (spoiler: lots of love).",
            "metadata": {
                "platform": "instagram",
                "status": "draft",
                "tone": "casual",
                "topic": "behind the scenes",
                "scheduled_at": "",
                "created_at": _now_iso(),
                "engagement": 45
            }
        },
        {
            "id": str(uuid.uuid4()),
            "document": "We hit 10k followers! Thank you for being on this journey with us.",
            "metadata": {
                "platform": "twitter",
                "status": "scheduled",
                "tone": "inspirational",
                "topic": "milestone",
                "scheduled_at": (datetime.utcnow().isoformat()),
                "created_at": _now_iso(),
                "engagement": 500
            }
        },
        {
            "id": str(uuid.uuid4()),
            "document": "How to create engaging carousels for Instagram that tell a story.",
            "metadata": {
                "platform": "instagram",
                "status": "published",
                "tone": "professional",
                "topic": "instagram",
                "scheduled_at": "",
                "created_at": _now_iso(),
                "engagement": 310
            }
        },
        {
            "id": str(uuid.uuid4()),
            "document": "Sunday reading: our top 3 books for startup founders.",
            "metadata": {
                "platform": "linkedin",
                "status": "draft",
                "tone": "inspirational",
                "topic": "books",
                "scheduled_at": "",
                "created_at": _now_iso(),
                "engagement": 78
            }
        }
    ]

    ids = [s["id"] for s in samples]
    documents = [s["document"] for s in samples]
    metadatas = [s["metadata"] for s in samples]
    embeddings = embed_texts(documents)
    _collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

def add_post(content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Embed and add a post to the collection."""
    global _collection
    if _collection is None:
        init_db()
    _id = str(uuid.uuid4())
    vec = embed_text(content)
    meta = metadata.copy()
    meta.setdefault("created_at", _now_iso())
    meta.setdefault("engagement", 0)
    _collection.add(ids=[_id], documents=[content], metadatas=[meta], embeddings=[vec])
    return {"id": _id, "document": content, "metadata": meta}

def get_all_posts(filters: Dict[str, Any] = {}) -> List[Dict[str, Any]]:
    if _collection is None:
        init_db()
    # list all and filter in Python
    res = _collection.get(include=['ids','documents','metadatas'])
    out = []
    for i, _id in enumerate(res['ids']):
        meta = res['metadatas'][i]
        doc = res['documents'][i]
        ok = True
        for k, v in filters.items():
            if k not in meta or (v != "" and meta.get(k) != v):
                ok = False
                break
        if ok:
            out.append({"id": _id, "document": doc, "metadata": meta})
    return out

def get_post_by_id(id: str) -> Optional[Dict[str, Any]]:
    if _collection is None:
        init_db()
    try:
        res = _collection.get(ids=[id], include=['ids','documents','metadatas'])
        if len(res['ids']) == 0:
            return None
        return {"id": res['ids'][0], "document": res['documents'][0], "metadata": res['metadatas'][0]}
    except Exception:
        return None

def update_post(id: str, content: str, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if _collection is None:
        init_db()
    # Remove and re-add with same id for simplicity
    delete_post(id)
    vec = embed_text(content)
    _collection.add(ids=[id], documents=[content], metadatas=[metadata], embeddings=[vec])
    return {"id": id, "document": content, "metadata": metadata}

def delete_post(id: str) -> bool:
    if _collection is None:
        init_db()
    try:
        _collection.delete(ids=[id])
        return True
    except Exception:
        return False

def semantic_search(query: str, n: int = 5) -> List[Dict[str, Any]]:
    if _collection is None:
        init_db()
    qvec = embed_text(query)
    results = _collection.query(query_embeddings=[qvec], n_results=n, include=['ids','documents','metadatas','distances'])
    out = []
    if len(results.get('ids', [])) == 0:
        return out
    ids = results['ids'][0]
    docs = results['documents'][0]
    metas = results['metadatas'][0]
    dists = results.get('distances', [[]])[0]
    for i, _id in enumerate(ids):
        out.append({"id": _id, "document": docs[i], "metadata": metas[i], "distance": dists[i] if i < len(dists) else None})
    return out

def get_similar_posts(content: str, n: int = 3) -> List[Dict[str, Any]]:
    return semantic_search(content, n=n)

def get_stats() -> Dict[str, Any]:
    if _collection is None:
        init_db()
    all_posts = get_all_posts()
    total = len(all_posts)
    by_status = {}
    by_platform = {}
    total_engagement = 0
    for p in all_posts:
        status = p['metadata'].get('status','draft')
        platform = p['metadata'].get('platform','unknown')
        by_status[status] = by_status.get(status, 0) + 1
        by_platform[platform] = by_platform.get(platform, 0) + 1
        total_engagement += int(p['metadata'].get('engagement', 0) or 0)
    engagement_rate = (total_engagement / max(total,1))
    return {
        "total": total,
        "by_status": by_status,
        "by_platform": by_platform,
        "engagement_rate": engagement_rate
    }
