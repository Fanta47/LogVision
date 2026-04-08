# ETL: Elasticsearch -> PostgreSQL

## 1) Create schema

```powershell
psql -h <pg_host> -U <pg_user> -d <pg_db> -f etl/postgres_schema.sql
```

## 2) Install deps

```powershell
python -m pip install -r etl/requirements.txt
```

## 3) Run ETL

```powershell
$env:ES_URL='https://localhost:9201'
$env:ES_USER='elastic'
$env:ES_PASSWORD='changeme123'
$env:ES_INDEX_PATTERN='log-unified-*'

$env:PG_HOST='localhost'
$env:PG_PORT='5432'
$env:PG_DB='logs'
$env:PG_USER='postgres'
$env:PG_PASSWORD='postgres'

python etl/es_to_postgres_etl.py
```

## Notes

- Incremental and idempotent: watermark is stored in `logs.etl_watermark`.
- Upserts are keyed by `source_doc_id`.
- Dimension/fact model:
  - `logs.dim_application`
  - `logs.fact_log_event`
  - `logs.fact_sql_event`
  - `logs.fact_scheduler_event`
  - `logs.fact_error_event`

