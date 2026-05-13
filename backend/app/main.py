from fastapi import FastAPI

from app.api.routes import errors, events, health, search, upload_logs
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version='0.1.0',
    description='Backend API for structured log insights and search.',
)

app.include_router(health.router)
app.include_router(events.router)
app.include_router(errors.router)
app.include_router(search.router)
app.include_router(upload_logs.router)


@app.get('/', tags=['meta'])
def root() -> dict:
    return {
        'service': settings.app_name,
        'environment': settings.app_env,
        'docs_url': '/docs',
        'future_modules': ['auth', 'alerts', 'predictions'],
    }
