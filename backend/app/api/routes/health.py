from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db_session
from app.schemas.responses import HealthResponse
from app.services.health_service import check_database_health

router = APIRouter(tags=['health'])


@router.get('/health', response_model=HealthResponse)
def health(db: Session = Depends(get_db_session)) -> HealthResponse:
    settings = get_settings()
    database_status = 'up'

    try:
        check_database_health(db)
    except Exception:
        database_status = 'down'

    overall_status = 'ok' if database_status == 'up' else 'degraded'
    return HealthResponse(
        status=overall_status,
        app_name=settings.app_name,
        environment=settings.app_env,
        database=database_status,
    )
