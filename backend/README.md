# LogVision Backend

This backend service provides a first production-style FastAPI API layer on top of the existing structured data model already available in PostgreSQL, plus search access to Elasticsearch.

## Scope

The service is intentionally focused on:
- Reading structured events from `base_event`
- Reading structured error events from `base_event` + `error_event`
- Basic log search through Elasticsearch
- Health checks for service and PostgreSQL connectivity

It is prepared with placeholders for future modules:
- Auth
- Alerts
- Predictions / ML integration

## Project Structure

```text
backend/
  app/
    api/routes/
    core/
    db/
    models/
    schemas/
    services/
    main.py
  tests/
  requirements.txt
  .env.example
  Dockerfile
  README.md
```

## Local Setup

1. Create a virtual environment:

```powershell
cd backend
python -m venv .venv
```

2. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Create `.env` from the example and adjust values if needed:

```powershell
Copy-Item .env.example .env
```

5. Run locally:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Run

From `backend/`:

```powershell
docker build -t logvision-backend:dev .
docker run --rm -p 8000:8000 --env-file .env logvision-backend:dev
```

## Initial Endpoints

- `GET /`
- `GET /health`
- `GET /events`
- `GET /errors`
- `GET /search/logs`

Interactive docs:
- `GET /docs`
- `GET /redoc`
