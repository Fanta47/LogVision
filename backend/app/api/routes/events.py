from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.responses import BaseEventResponse
from app.services.event_service import fetch_recent_events

router = APIRouter(prefix='/events', tags=['events'])


@router.get('', response_model=list[BaseEventResponse])
def get_events(
    application_key: str | None = None,
    log_family: str | None = None,
    event_type: str | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db_session),
) -> list[BaseEventResponse]:
    rows = fetch_recent_events(
        db=db,
        application_key=application_key,
        log_family=log_family,
        event_type=event_type,
        from_ts=from_ts,
        to_ts=to_ts,
        limit=limit,
    )
    return [BaseEventResponse(**row) for row in rows]
