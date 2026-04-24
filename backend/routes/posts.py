from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from vector_db import add_post, get_all_posts, get_post_by_id, update_post, delete_post, semantic_search, get_similar_posts

router = APIRouter()


class PostCreate(BaseModel):
    content: str
    metadata: Dict[str, Any]


class PostUpdate(BaseModel):
    content: str
    metadata: Dict[str, Any]


@router.post("/api/posts")
async def create_post(p: PostCreate):
    return add_post(p.content, p.metadata)


@router.get("/api/posts")
async def list_posts(platform: Optional[str] = None, status: Optional[str] = None):
    filters = {}
    if platform:
        filters['platform'] = platform
    if status:
        filters['status'] = status
    return get_all_posts(filters=filters)


@router.get("/api/posts/search")
async def search_posts(q: str = Query(...), n: int = 5):
    return semantic_search(q, n=n)


@router.post("/api/posts/search/similar")
async def similar_posts(payload: Dict[str, str]):
    content = payload.get('content','')
    return get_similar_posts(content, n=3)


@router.get("/api/posts/{id}")
async def get_post(id: str):
    p = get_post_by_id(id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return p


@router.put("/api/posts/{id}")
async def put_post(id: str, upd: PostUpdate):
    p = update_post(id, upd.content, upd.metadata)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    return p


@router.delete("/api/posts/{id}")
async def del_post(id: str):
    ok = delete_post(id)
    return {"ok": ok}


@router.post("/api/posts/{id}/publish")
async def publish_post(id: str):
    p = get_post_by_id(id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    meta = p['metadata']
    meta['status'] = 'published'
    meta['scheduled_at'] = meta.get('scheduled_at','') or ''
    update_post(id, p['document'], meta)
    return {"ok": True}
