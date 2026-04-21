from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session


def _build_filters(
    application_key: str | None,
    log_family: str | None,
    event_type: str | None,
    from_ts: datetime | None,
    to_ts: datetime | None,
) -> tuple[list[str], dict[str, object]]:
    conditions: list[str] = []
    params: dict[str, object] = {}

    if application_key:
        conditions.append('be.application_key = :application_key')
        params['application_key'] = application_key
    if log_family:
        conditions.append('be.log_family = :log_family')
        params['log_family'] = log_family
    if event_type:
        conditions.append('be.event_type = :event_type')
        params['event_type'] = event_type
    if from_ts:
        conditions.append('be.event_ts >= :from_ts')
        params['from_ts'] = from_ts
    if to_ts:
        conditions.append('be.event_ts <= :to_ts')
        params['to_ts'] = to_ts

    return conditions, params


def fetch_recent_events(
    db: Session,
    application_key: str | None = None,
    log_family: str | None = None,
    event_type: str | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    limit: int = 100,
) -> list[dict]:
    conditions, params = _build_filters(application_key, log_family, event_type, from_ts, to_ts)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''

    query = text(
        f"""
        SELECT
            be.event_id,
            be.event_ts,
            be.application_key,
            be.log_family,
            be.event_type,
            be.severity,
            be.raw_message
        FROM base_event be
        {where_clause}
        ORDER BY be.event_ts DESC
        LIMIT :limit
        """
    )
    params['limit'] = limit

    rows = db.execute(query, params).mappings().all()
    return [dict(row) for row in rows]


def fetch_recent_errors(
    db: Session,
    application_key: str | None = None,
    log_family: str | None = None,
    event_type: str | None = None,
    from_ts: datetime | None = None,
    to_ts: datetime | None = None,
    limit: int = 100,
) -> list[dict]:
    conditions, params = _build_filters(application_key, log_family, event_type, from_ts, to_ts)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ''

    query = text(
        f"""
        SELECT
            be.event_id,
            be.event_ts,
            be.application_key,
            be.log_family,
            ee.error_code,
            ee.error_type,
            ee.error_message
        FROM base_event be
        INNER JOIN error_event ee ON ee.event_id = be.event_id
        {where_clause}
        ORDER BY be.event_ts DESC
        LIMIT :limit
        """
    )
    params['limit'] = limit

    rows = db.execute(query, params).mappings().all()
    return [dict(row) for row in rows]
