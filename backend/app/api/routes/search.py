from fastapi import APIRouter, Query

from app.services.search_service import search_logs

router = APIRouter(prefix='/search', tags=['search'])


@router.get('/logs')
def search_logs_endpoint(
    term: str | None = Query(default=None, description='Simple query string to search in logs.'),
    size: int = Query(default=20, ge=1, le=200),
) -> dict:
    return search_logs(term=term, size=size)
