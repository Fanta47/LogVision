import hashlib
import os
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import execute_batch
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import BadRequestError

ES_URLS_RAW = os.getenv("ES_URLS", os.getenv("ES_URL", "https://es01:9200"))
ES_URLS = [u.strip() for u in ES_URLS_RAW.split(",") if u.strip()]
ES_INDEX = os.getenv("ES_INDEX", "logvision-events-*")
ES_USERNAME = os.getenv("ES_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "changeme123")
ES_CA_CERT = os.getenv("ES_CA_CERT", "/certs/ca/ca.crt")
PG_DSN = os.getenv("PG_DSN", "postgresql://logs_user:logs_pass@postgres:5432/logs")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "5"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "500"))
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "es_to_pg")
FULL_SYNC_ON_START = os.getenv("FULL_SYNC_ON_START", "false").lower() in ("1", "true", "yes", "on")

DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
NUM_RE = re.compile(r"\b\d+\b")
PATH_RE = re.compile(r"([A-Za-z]:\\[^\s]+|/[^\s]+)")
HEX_RE = re.compile(r"\b[a-fA-F0-9]{12,}\b")
SPACE_RE = re.compile(r"\s+")


def parse_ts(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def normalize_details(text: Optional[str]) -> str:
    if not text:
        return ""
    out = DATE_RE.sub("<DATE>", text)
    out = IP_RE.sub("<IP>", out)
    out = PATH_RE.sub("<PATH>", out)
    out = HEX_RE.sub("<HEX>", out)
    out = NUM_RE.sub("<NUM>", out)
    return SPACE_RE.sub(" ", out).strip()


def build_event_uid(d: Dict[str, Any]) -> str:
    parts = [
        str(d.get("@timestamp", "")),
        str(d.get("application_key", "")),
        str(d.get("component_name", "")),
        str(d.get("thread_name", "")),
        str(d.get("details", "")),
        str(d.get("source_path", "")),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def get_watermark(conn) -> Tuple[datetime, str]:
    with conn.cursor() as cur:
        cur.execute("SELECT last_event_timestamp, last_source_doc_id FROM etl_watermark WHERE pipeline_name=%s", (PIPELINE_NAME,))
        row = cur.fetchone()
        if row:
            return row[0], row[1]
    return datetime(1970, 1, 1, tzinfo=timezone.utc), ""


def ensure_schema(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS etl_watermark (
              pipeline_name VARCHAR(128) PRIMARY KEY,
              last_event_timestamp TIMESTAMPTZ NOT NULL DEFAULT '1970-01-01 00:00:00+00',
              last_source_doc_id TEXT NOT NULL DEFAULT '',
              updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            ALTER TABLE base_event
              ADD COLUMN IF NOT EXISTS id BIGSERIAL,
              ADD COLUMN IF NOT EXISTS event_uid VARCHAR(128),
              ADD COLUMN IF NOT EXISTS es_id VARCHAR(256),
              ADD COLUMN IF NOT EXISTS upload_uid VARCHAR(128),
              ADD COLUMN IF NOT EXISTS application_key VARCHAR(100),
              ADD COLUMN IF NOT EXISTS component_name VARCHAR(150),
              ADD COLUMN IF NOT EXISTS platform VARCHAR(120),
              ADD COLUMN IF NOT EXISTS environment VARCHAR(120),
              ADD COLUMN IF NOT EXISTS scope VARCHAR(120),
              ADD COLUMN IF NOT EXISTS thread_name VARCHAR(255),
              ADD COLUMN IF NOT EXISTS normalized_details TEXT,
              ADD COLUMN IF NOT EXISTS details_hash VARCHAR(128),
              ADD COLUMN IF NOT EXISTS source_path TEXT,
              ADD COLUMN IF NOT EXISTS stored_file_name VARCHAR(255),
              ADD COLUMN IF NOT EXISTS original_file_name VARCHAR(255),
              ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW()
            """
        )
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_base_event_event_uid ON base_event(event_uid)")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sla_event (
              base_event_id BIGINT PRIMARY KEY,
              caller_class TEXT,
              caller_method TEXT,
              caller_line INT,
              sla_class_name TEXT,
              context_raw TEXT,
              sla_status VARCHAR(32),
              sla_result_pk TEXT
            )
            """
        )
        cur.execute(
            """
            ALTER TABLE sql_event
              ADD COLUMN IF NOT EXISTS base_event_id BIGINT,
              ADD COLUMN IF NOT EXISTS sql_query TEXT,
              ADD COLUMN IF NOT EXISTS normalized_sql_query TEXT,
              ADD COLUMN IF NOT EXISTS table_name TEXT,
              ADD COLUMN IF NOT EXISTS query_length INT,
              ADD COLUMN IF NOT EXISTS estimated_complexity_score NUMERIC(10,4)
            """
        )


def set_watermark(conn, ts: datetime, doc_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO etl_watermark(pipeline_name, last_event_timestamp, last_source_doc_id, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (pipeline_name) DO UPDATE
            SET last_event_timestamp=EXCLUDED.last_event_timestamp,
                last_source_doc_id=EXCLUDED.last_source_doc_id,
                updated_at=NOW()
            """,
            (PIPELINE_NAME, ts, doc_id),
        )


def fetch_batch(es: Elasticsearch, after: Optional[List[Any]], last_ts: datetime):
    query = {
        "size": BATCH_SIZE,
        "sort": [
            {"@timestamp": {"order": "asc", "format": "strict_date_optional_time_nanos"}},
            {"_doc": {"order": "asc"}},
        ],
        "query": {"range": {"@timestamp": {"gte": last_ts.isoformat()}}},
    }
    if after:
        query["search_after"] = after
    try:
        return es.search(index=ES_INDEX, body=query, ignore_unavailable=True, allow_no_indices=True)
    except BadRequestError as exc:
        print(f"ES search failed. index={ES_INDEX} sort={query['sort']} after={after} error={exc}", flush=True)
        raise


def upsert_rows(conn, rows: List[Dict[str, Any]]) -> Tuple[datetime, str, int]:
    inserted = 0
    sql_rows = []
    sla_rows = []
    last_ts = datetime(1970, 1, 1, tzinfo=timezone.utc)
    last_id = ""

    with conn.cursor() as cur:
        for d in rows:
            es_id = d.get("_id", "")
            src = d.get("_source", {})
            ts_raw = src.get("@timestamp")
            if not ts_raw:
                continue
            ts = parse_ts(ts_raw)
            app_key = src.get("application_key") or src.get("application_name") or "unknown_app"
            component = src.get("component_name") or src.get("application_group") or "unknown_component"
            log_family = src.get("log_family") or "unknown"
            event_type = src.get("event_type") or "unknown"
            parse_status = src.get("parse_status") or "ok"
            parse_confidence = src.get("parse_confidence") or "1.0"
            event_uid = build_event_uid(src)
            source_doc_id = event_uid  # Use event_uid as primary key
            details = src.get("details", "")
            normalized = normalize_details(details)
            details_hash = hashlib.sha256((details or "").encode("utf-8")).hexdigest()

            cur.execute(
                """
                INSERT INTO base_event(
                  event_uid, es_id, source_doc_id, upload_uid, event_timestamp, application_key, component_name,
                  application_name, application_group, parse_status, parse_confidence,
                  platform, environment, scope, log_level, log_family, event_type, thread_name,
                  details, normalized_details, details_hash, source_path, stored_file_name, original_file_name, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (event_uid) DO NOTHING
                RETURNING id
                """,
                (
                    event_uid,
                    es_id,
                    source_doc_id,
                    src.get("upload_uid"),
                    ts,
                    app_key,
                    component,
                    app_key,
                    component,
                    parse_status,
                    parse_confidence,
                    src.get("platform"),
                    src.get("environment"),
                    src.get("scope"),
                    src.get("log_level"),
                    log_family,
                    event_type,
                    src.get("thread_name"),
                    details,
                    normalized,
                    details_hash,
                    src.get("source_path"),
                    src.get("stored_file_name"),
                    src.get("original_file_name"),
                ),
            )
            row = cur.fetchone()
            cur.execute(
                """
                UPDATE base_event
                SET application_name = COALESCE(application_name, %s),
                    application_group = COALESCE(application_group, %s),
                    log_family = COALESCE(log_family, %s),
                    event_type = COALESCE(event_type, %s),
                    parse_status = COALESCE(parse_status, %s),
                    parse_confidence = COALESCE(parse_confidence, %s)
                WHERE event_uid = %s
                """,
                (app_key, component, log_family, event_type, parse_status, parse_confidence, event_uid),
            )
            if not row:
                continue

            base_event_id = row[0]
            inserted += 1
            if log_family == "persistence":
                sql_query = src.get("sql_query")
                normalized_sql_query = normalize_details(sql_query)
                qlen = len(sql_query) if sql_query else 0
                sql_rows.append((base_event_id, src.get("event_type"), sql_query, normalized_sql_query, src.get("table_name"), src.get("result_size"), src.get("data_source"), qlen, min(1.0, qlen / 2000.0)))
            elif log_family == "sla":
                sla_rows.append((base_event_id, src.get("caller_class"), src.get("caller_method"), src.get("caller_line"), src.get("sla_class_name"), src.get("context_raw"), src.get("sla_status"), src.get("sla_result_pk")))

            if src.get("upload_uid"):
                cur.execute("UPDATE log_upload SET status='processed' WHERE upload_uid=%s", (src.get("upload_uid"),))

            last_ts = ts
            last_id = es_id

        if sql_rows:
            execute_batch(cur, """
                INSERT INTO sql_event(base_event_id, sql_operation, sql_query, normalized_sql_query, table_name, result_size, data_source, query_length, estimated_complexity_score)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (base_event_id) DO NOTHING
            """, sql_rows, page_size=200)

        if sla_rows:
            execute_batch(cur, """
                INSERT INTO sla_event(base_event_id, caller_class, caller_method, caller_line, sla_class_name, context_raw, sla_status, sla_result_pk)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (base_event_id) DO NOTHING
            """, sla_rows, page_size=200)

    return last_ts, last_id, inserted


def main():
    print(
        f"Starting ETL with ES_INDEX={ES_INDEX}, ES_URLS={ES_URLS}, PG_DSN={PG_DSN}, PIPELINE_NAME={PIPELINE_NAME}, BATCH_SIZE={BATCH_SIZE}",
        flush=True,
    )
    es = Elasticsearch(ES_URLS, basic_auth=(ES_USERNAME, ES_PASSWORD), ca_certs=ES_CA_CERT, verify_certs=True)
    full_sync_done = False
    while True:
        try:
            with psycopg2.connect(PG_DSN) as conn:
                conn.autocommit = False
                ensure_schema(conn)
                if FULL_SYNC_ON_START and not full_sync_done:
                    set_watermark(conn, datetime(1970, 1, 1, tzinfo=timezone.utc), "")
                    print("FULL_SYNC_ON_START=true -> watermark reset to epoch", flush=True)
                    conn.commit()
                    full_sync_done = True
                last_ts, last_id = get_watermark(conn)
                after = None
                moved = 0
                while True:
                    res = fetch_batch(es, after, last_ts)
                    hits = res.get("hits", {}).get("hits", [])
                    if not hits:
                        break
                    ts, doc_id, inserted = upsert_rows(conn, hits)
                    if inserted > 0:
                        set_watermark(conn, ts, doc_id or last_id)
                    conn.commit()
                    moved += inserted
                    after = hits[-1].get("sort")
                print(f"ETL cycle complete. moved={moved}", flush=True)
        except Exception as exc:
            print(f"ETL error: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
