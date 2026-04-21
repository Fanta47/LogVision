from datetime import datetime

from pydantic import BaseModel


class BaseEventResponse(BaseModel):
    event_id: int
    event_ts: datetime
    application_key: str | None = None
    log_family: str | None = None
    event_type: str | None = None
    severity: str | None = None
    raw_message: str | None = None


class ErrorEventResponse(BaseModel):
    event_id: int
    event_ts: datetime
    application_key: str | None = None
    log_family: str | None = None
    error_code: str | None = None
    error_type: str | None = None
    error_message: str | None = None


class HealthResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    database: str
