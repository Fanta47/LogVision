import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Tuple

import urllib3
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan
import psycopg2
from psycopg2.extras import execute_batch

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ES_URL = os.getenv("ES_URL", "https://localhost:9201")
ES_USER = os.getenv("ES_USER", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "changeme123")
ES_INDEX_PATTERN = os.getenv("ES_INDEX_PATTERN", "log-unified-*")

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB", "logs")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")

PIPELINE_NAME = os.getenv("ETL_PIPELINE_NAME", "es_to_pg_logs")
BATCH_SIZE = int(os.getenv("ETL_BATCH_SIZE", "500"))


def parse_ts(value: str) -> datetime:
  if value.endswith("Z"):
    value = value[:-1] + "+00:00"
  dt = datetime.fromisoformat(value)
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
  return dt


def bool_or_none(value: Any) -> Any:
  if value in (True, False):
    return value
  if value is None:
    return None
  text = str(value).strip().lower()
  if text == "true":
    return True
  if text == "false":
    return False
  return None


def int_or_none(value: Any) -> Any:
  if value is None or value == "":
    return None
  try:
    return int(value)
  except (TypeError, ValueError):
    return None


def get_pg_connection():
  return psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    dbname=PG_DB,
    user=PG_USER,
    password=PG_PASSWORD,
  )


def get_watermark(conn) -> Tuple[datetime, str]:
  with conn.cursor() as cur:
    cur.execute(
      """
      SELECT last_event_timestamp, last_source_doc_id
      FROM logs.etl_watermark
      WHERE pipeline_name = %s
      """,
      (PIPELINE_NAME,),
    )
    row = cur.fetchone()
    if row:
      return row[0], row[1]
  return datetime(1970, 1, 1, tzinfo=timezone.utc), ""


def update_watermark(conn, event_ts: datetime, source_doc_id: str) -> None:
  with conn.cursor() as cur:
    cur.execute(
      """
      INSERT INTO logs.etl_watermark(pipeline_name, last_event_timestamp, last_source_doc_id, updated_at)
      VALUES (%s, %s, %s, NOW())
      ON CONFLICT (pipeline_name) DO UPDATE
      SET last_event_timestamp = EXCLUDED.last_event_timestamp,
          last_source_doc_id = EXCLUDED.last_source_doc_id,
          updated_at = NOW()
      """,
      (PIPELINE_NAME, event_ts, source_doc_id),
    )


def build_query(last_ts: datetime, last_id: str) -> Dict[str, Any]:
  return {
    "sort": [
      {"@timestamp": {"order": "asc", "format": "strict_date_optional_time_nanos"}},
      {"source_doc_id.keyword": {"order": "asc"}},
    ],
    "query": {
      "bool": {
        "filter": [
          {
            "bool": {
              "should": [
                {"range": {"@timestamp": {"gt": last_ts.isoformat()}}},
                {
                  "bool": {
                    "must": [
                      {"term": {"@timestamp": last_ts.isoformat()}},
                      {"range": {"source_doc_id.keyword": {"gt": last_id}}},
                    ]
                  }
                },
              ],
              "minimum_should_match": 1,
            }
          }
        ]
      }
    },
  }


def stream_docs(es: Elasticsearch, last_ts: datetime, last_id: str) -> Iterable[Dict[str, Any]]:
  query = build_query(last_ts, last_id)
  for hit in scan(
    client=es,
    index=ES_INDEX_PATTERN,
    query=query,
    size=BATCH_SIZE,
    preserve_order=True,
    clear_scroll=True,
  ):
    src = hit.get("_source", {})
    src_doc_id = src.get("source_doc_id")
    ts = src.get("@timestamp")
    if src_doc_id and ts:
      yield src


def to_rows(docs: List[Dict[str, Any]]):
  apps = {}
  fact_rows = []
  sql_rows = []
  sched_rows = []
  error_rows = []

  for d in docs:
    app_key = (d.get("application_key") or "unknown").strip() or "unknown"
    apps[app_key] = (
      app_key,
      d.get("application_name") or "unknown_application",
      d.get("application_group") or "unknown",
    )

    fact_rows.append(
      (
        d.get("source_doc_id"),
        parse_ts(d["@timestamp"]),
        app_key,
        d.get("log_level"),
        d.get("log_origin"),
        d.get("thread"),
        d.get("log_family"),
        d.get("event_type"),
        d.get("parse_status"),
        d.get("parse_confidence"),
        d.get("analysis_status"),
        d.get("source_file"),
        d.get("details"),
        d.get("context"),
      )
    )

    if d.get("log_family") == "sql_persistence":
      sql_rows.append(
        (
          d.get("source_doc_id"),
          d.get("query_stage"),
          d.get("query_text"),
          d.get("sql_operation"),
          d.get("sql_table"),
          bool_or_none(d.get("query_has_placeholders")),
          d.get("main_entity_id"),
          d.get("sql_entity_family"),
          int_or_none(d.get("result_size")),
          int_or_none(d.get("update_count")),
          d.get("data_source"),
        )
      )

    if d.get("log_family") == "scheduler_controller":
      sched_rows.append(
        (
          d.get("source_doc_id"),
          int_or_none(d.get("worker_id")),
          d.get("criterion"),
          d.get("controller_name"),
          d.get("method_name"),
          d.get("method_display_name"),
          d.get("service_domain"),
        )
      )

    if d.get("log_family") == "application_error":
      error_rows.append(
        (
          d.get("source_doc_id"),
          d.get("error_message"),
          d.get("exception_class"),
          d.get("root_exception_class"),
          d.get("error_keyword"),
          int_or_none(d.get("caused_by_count")),
          d.get("stack_trace"),
        )
      )

  return list(apps.values()), fact_rows, sql_rows, sched_rows, error_rows


def upsert_batch(conn, docs: List[Dict[str, Any]]) -> Tuple[datetime, str]:
  apps, fact_rows, sql_rows, sched_rows, error_rows = to_rows(docs)

  with conn.cursor() as cur:
    execute_batch(
      cur,
      """
      INSERT INTO logs.dim_application(application_key, application_name, application_group, first_seen_at, last_seen_at)
      VALUES (%s, %s, %s, NOW(), NOW())
      ON CONFLICT (application_key) DO UPDATE
      SET application_name = EXCLUDED.application_name,
          application_group = EXCLUDED.application_group,
          last_seen_at = NOW()
      """,
      apps,
      page_size=500,
    )

    execute_batch(
      cur,
      """
      INSERT INTO logs.fact_log_event(
        source_doc_id, event_timestamp, application_key, log_level, log_origin, thread,
        log_family, event_type, parse_status, parse_confidence, analysis_status,
        source_file, details, context
      )
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      ON CONFLICT (source_doc_id) DO UPDATE
      SET event_timestamp = EXCLUDED.event_timestamp,
          application_key = EXCLUDED.application_key,
          log_level = EXCLUDED.log_level,
          log_origin = EXCLUDED.log_origin,
          thread = EXCLUDED.thread,
          log_family = EXCLUDED.log_family,
          event_type = EXCLUDED.event_type,
          parse_status = EXCLUDED.parse_status,
          parse_confidence = EXCLUDED.parse_confidence,
          analysis_status = EXCLUDED.analysis_status,
          source_file = EXCLUDED.source_file,
          details = EXCLUDED.details,
          context = EXCLUDED.context
      """,
      fact_rows,
      page_size=500,
    )

    if sql_rows:
      execute_batch(
        cur,
        """
        INSERT INTO logs.fact_sql_event(
          source_doc_id, query_stage, query_text, sql_operation, sql_table,
          query_has_placeholders, main_entity_id, sql_entity_family,
          result_size, update_count, data_source
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_doc_id) DO UPDATE
        SET query_stage = EXCLUDED.query_stage,
            query_text = EXCLUDED.query_text,
            sql_operation = EXCLUDED.sql_operation,
            sql_table = EXCLUDED.sql_table,
            query_has_placeholders = EXCLUDED.query_has_placeholders,
            main_entity_id = EXCLUDED.main_entity_id,
            sql_entity_family = EXCLUDED.sql_entity_family,
            result_size = EXCLUDED.result_size,
            update_count = EXCLUDED.update_count,
            data_source = EXCLUDED.data_source
        """,
        sql_rows,
        page_size=500,
      )

    if sched_rows:
      execute_batch(
        cur,
        """
        INSERT INTO logs.fact_scheduler_event(
          source_doc_id, worker_id, criterion, controller_name, method_name,
          method_display_name, service_domain
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_doc_id) DO UPDATE
        SET worker_id = EXCLUDED.worker_id,
            criterion = EXCLUDED.criterion,
            controller_name = EXCLUDED.controller_name,
            method_name = EXCLUDED.method_name,
            method_display_name = EXCLUDED.method_display_name,
            service_domain = EXCLUDED.service_domain
        """,
        sched_rows,
        page_size=500,
      )

    if error_rows:
      execute_batch(
        cur,
        """
        INSERT INTO logs.fact_error_event(
          source_doc_id, error_message, exception_class, root_exception_class,
          error_keyword, caused_by_count, stack_trace
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (source_doc_id) DO UPDATE
        SET error_message = EXCLUDED.error_message,
            exception_class = EXCLUDED.exception_class,
            root_exception_class = EXCLUDED.root_exception_class,
            error_keyword = EXCLUDED.error_keyword,
            caused_by_count = EXCLUDED.caused_by_count,
            stack_trace = EXCLUDED.stack_trace
        """,
        error_rows,
        page_size=500,
      )

  last_doc = docs[-1]
  return parse_ts(last_doc["@timestamp"]), last_doc["source_doc_id"]


def main():
  es = Elasticsearch(
    ES_URL,
    basic_auth=(ES_USER, ES_PASSWORD),
    verify_certs=False,
    request_timeout=60,
  )

  with get_pg_connection() as conn:
    conn.autocommit = False
    last_ts, last_id = get_watermark(conn)

    batch: List[Dict[str, Any]] = []
    moved = 0

    for doc in stream_docs(es, last_ts, last_id):
      batch.append(doc)
      if len(batch) >= BATCH_SIZE:
        new_ts, new_id = upsert_batch(conn, batch)
        update_watermark(conn, new_ts, new_id)
        conn.commit()
        moved += len(batch)
        print(f"Committed {moved} rows (watermark={new_ts.isoformat()}|{new_id})")
        batch.clear()

    if batch:
      new_ts, new_id = upsert_batch(conn, batch)
      update_watermark(conn, new_ts, new_id)
      conn.commit()
      moved += len(batch)

    print(f"ETL complete. moved_rows={moved}")


if __name__ == "__main__":
  main()
