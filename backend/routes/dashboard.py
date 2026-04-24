from fastapi import APIRouter
from vector_db import get_stats

router = APIRouter()


@router.get("/api/dashboard/stats")
async def stats():
    return get_stats()
