from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine

from .config import settings


def _make_engine() -> Optional:
    user = settings.PG_USER
    pwd = settings.PG_PASSWORD
    host = settings.PG_HOST
    port = settings.PG_PORT
    db = settings.PG_DB
    if not all([user, pwd, host, port, db]):
        return None
    url = f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"
    return create_engine(url)


ENGINE = None
try:
    ENGINE = _make_engine()
except Exception:
    ENGINE = None


def query_to_df(sql: str) -> pd.DataFrame:
    """Execute SQL and return a pandas DataFrame.

    Raises:
        RuntimeError: if no DB engine is configured.
    """
    if ENGINE is None:
        raise RuntimeError("No database engine configured. Check environment variables.")
    return pd.read_sql(sql, ENGINE)


def get_events_sample() -> pd.DataFrame:
    """Return a sample combined events DataFrame (try DB, caller may fallback)."""
    sql = """
    SELECT created_at as timestamp, application_key, level, host, username as "user", message
    FROM base_event
    UNION ALL
    SELECT created_at, application_key, level, host, username, message FROM error_event
    UNION ALL
    SELECT created_at, application_key, level, host, username, message FROM sql_event
    UNION ALL
    SELECT created_at, application_key, level, host, username, message FROM scheduler_controller_event
    ORDER BY timestamp
    LIMIT 10000
    """
    return query_to_df(sql)
