import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import execute_batch
from elasticsearch import Elasticsearch

ES_URL = os.getenv("ES_URL", "https://es01:9200")
ES_INDEX = os.getenv("ES_INDEX", "log-unified-*")
ES_USERNAME = os.getenv("ES_USERNAME", "elastic")
ES_PASSWORD = os.getenv("ES_PASSWORD", "changeme123")
ES_CA_CERT = os.getenv("ES_CA_CERT", "/certs/ca/ca.crt")

PG_DSN = os.getenv("PG_DSN", "postgresql://logs_user:logs_pass@postgres:5432/logs")
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "5"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1000"))
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "es_to_pg")


def parse_ts(value: str) -> datetime:
  if value.endswith("Z"):
    value = value[:-1] + "+00:00"
  dt = datetime.fromisoformat(value)
  if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
  return dt


def bool_or_none(v: Any) -> Optional[bool]:
  if v is None:
    return None
  if isinstance(v, bool):
    return v
  s = str(v).strip().lower()
  if s == "true":
    return True
  if s == "false":
    return False
  return None


def int_or_none(v: Any) -> Optional[int]:
  if v in (None, ""):
    return None
  try:
    return int(v)
  except Exception:
    return None


def get_checkpoint(conn) -> Tuple[datetime, str]:
  with conn.cursor() as cur:
    cur.execute(
      """
      SELECT last_event_timestamp, last_source_doc_id
      FROM etl_checkpoint
      WHERE pipeline_name = %s
      """,
      (PIPELINE_NAME,),
    )
    row = cur.fetchone()
    if row:
      return row[0], row[1]
  return datetime(1970, 1, 1, tzinfo=timezone.utc), ""


def set_checkpoint(conn, ts: datetime, doc_id: str) -> None:
  with conn.cursor() as cur:
    cur.execute(
      """
      INSERT INTO etl_checkpoint(pipeline_name, last_event_timestamp, last_source_doc_id, updated_at)
      VALUES (%s, %s, %s, NOW())
      ON CONFLICT (pipeline_name) DO UPDATE
      SET last_event_timestamp = EXCLUDED.last_event_timestamp,
          last_source_doc_id = EXCLUDED.last_source_doc_id,
          updated_at = NOW()
      """,
      (PIPELINE_NAME, ts, doc_id),
    )


def upsert_rows(conn, rows: List[Dict[str, Any]]) -> Tuple[datetime, str]:
  base_rows = []
  sql_rows = []
  sched_rows = []
  err_rows = []

  for d in rows:
    base_rows.append(
      (
        d.get("source_doc_id"),
        parse_ts(d["@timestamp"]),
        d.get("application_name") or "unknown_application",
        d.get("application_key") or "unknown",
        d.get("application_group") or "unknown",
        d.get("log_level"),
        d.get("log_origin"),
        d.get("thread"),
        d.get("log_family") or "unknown",
        d.get("event_type") or "generic",
        d.get("parse_status") or "unknown",
        d.get("parse_confidence") or "unknown",
        d.get("analysis_status"),
        d.get("source_file"),
        d.get("context"),
        d.get("details"),
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
      err_rows.append(
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

  with conn.cursor() as cur:
    execute_batch(
      cur,
      """
      INSERT INTO base_event(
        source_doc_id, event_timestamp, application_name, application_key, application_group,
        log_level, log_origin, thread, log_family, event_type,
        parse_status, parse_confidence, analysis_status, source_file, context, details
      )
      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      ON CONFLICT (source_doc_id) DO UPDATE
      SET event_timestamp = EXCLUDED.event_timestamp,
          application_name = EXCLUDED.application_name,
          application_key = EXCLUDED.application_key,
          application_group = EXCLUDED.application_group,
          log_level = EXCLUDED.log_level,
          log_origin = EXCLUDED.log_origin,
          thread = EXCLUDED.thread,
          log_family = EXCLUDED.log_family,
          event_type = EXCLUDED.event_type,
          parse_status = EXCLUDED.parse_status,
          parse_confidence = EXCLUDED.parse_confidence,
          analysis_status = EXCLUDED.analysis_status,
          source_file = EXCLUDED.source_file,
          context = EXCLUDED.context,
          details = EXCLUDED.details
      """,
      base_rows,
      page_size=500,
    )

    if sql_rows:
      execute_batch(
        cur,
        """
        INSERT INTO sql_event(
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
        INSERT INTO scheduler_controller_event(
          source_doc_id, worker_id, criterion, controller_name,
          method_name, method_display_name, service_domain
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

    if err_rows:
      execute_batch(
        cur,
        """
        INSERT INTO error_event(
          source_doc_id, error_message, exception_class,
          root_exception_class, error_keyword, caused_by_count, stack_trace
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
        err_rows,
        page_size=500,
      )

  last = rows[-1]
  return parse_ts(last["@timestamp"]), last.get("source_doc_id", "")


def fetch_batch(es: Elasticsearch, pit_id: str, after: Optional[List[Any]], last_ts: datetime) -> Dict[str, Any]:
  query = {
    "size": BATCH_SIZE,
    "sort": [
      {"@timestamp": {"order": "asc", "format": "strict_date_optional_time_nanos"}},
      {"source_doc_id.keyword": {"order": "asc"}},
    ],
    "query": {
      "range": {
        "@timestamp": {
          "gte": last_ts.isoformat()
        }
      }
    },
    "pit": {
      "id": pit_id,
      "keep_alive": "2m"
    }
  }
  if after:
    query["search_after"] = after
  return es.search(body=query)


def run_once(es: Elasticsearch, conn) -> int:
  last_ts, last_id = get_checkpoint(conn)
  moved = 0

  pit = es.open_point_in_time(index=ES_INDEX, keep_alive="2m")
  pit_id = pit["id"]

  try:
    after = None
    batch_docs: List[Dict[str, Any]] = []

    while True:
      res = fetch_batch(es, pit_id, after, last_ts)
      hits = res.get("hits", {}).get("hits", [])
      if not hits:
        break

      for h in hits:
        src = h.get("_source", {})
        ts_raw = src.get("@timestamp")
        doc_id = src.get("source_doc_id")
        if not ts_raw or not doc_id:
          continue

        ts = parse_ts(ts_raw)
        if (ts, doc_id) <= (last_ts, last_id):
          continue

        batch_docs.append(src)

      if batch_docs:
        new_ts, new_id = upsert_rows(conn, batch_docs)
        set_checkpoint(conn, new_ts, new_id)
        conn.commit()
        moved += len(batch_docs)
        last_ts, last_id = new_ts, new_id
        batch_docs = []

      after = hits[-1].get("sort")

  finally:
    try:
      es.close_point_in_time(body={"id": pit_id})
    except Exception:
      pass

  return moved


def main() -> None:
  es = Elasticsearch(
    ES_URL,
    basic_auth=(ES_USERNAME, ES_PASSWORD),
    ca_certs=ES_CA_CERT,
    verify_certs=True,
    request_timeout=60,
  )

  while True:
    try:
      with psycopg2.connect(PG_DSN) as conn:
        conn.autocommit = False
        moved = run_once(es, conn)
      print(f"ETL cycle complete. moved={moved}", flush=True)
    except Exception as exc:
      print(f"ETL error: {exc}", flush=True)
    time.sleep(POLL_SECONDS)


if __name__ == "__main__":
  main()
