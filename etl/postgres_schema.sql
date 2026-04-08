CREATE SCHEMA IF NOT EXISTS logs;

CREATE TABLE IF NOT EXISTS logs.dim_application (
  application_key TEXT PRIMARY KEY,
  application_name TEXT NOT NULL,
  application_group TEXT NOT NULL,
  first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS logs.fact_log_event (
  source_doc_id TEXT PRIMARY KEY,
  event_timestamp TIMESTAMPTZ NOT NULL,
  application_key TEXT NOT NULL REFERENCES logs.dim_application(application_key),
  log_level TEXT,
  log_origin TEXT,
  thread TEXT,
  log_family TEXT,
  event_type TEXT,
  parse_status TEXT,
  parse_confidence TEXT,
  analysis_status TEXT,
  source_file TEXT,
  details TEXT,
  context TEXT,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fact_log_event_ts ON logs.fact_log_event(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_log_event_app_ts ON logs.fact_log_event(application_key, event_timestamp);
CREATE INDEX IF NOT EXISTS idx_fact_log_event_family ON logs.fact_log_event(log_family, event_type);

CREATE TABLE IF NOT EXISTS logs.fact_sql_event (
  source_doc_id TEXT PRIMARY KEY REFERENCES logs.fact_log_event(source_doc_id) ON DELETE CASCADE,
  query_stage TEXT,
  query_text TEXT,
  sql_operation TEXT,
  sql_table TEXT,
  query_has_placeholders BOOLEAN,
  main_entity_id TEXT,
  sql_entity_family TEXT,
  result_size INTEGER,
  update_count INTEGER,
  data_source TEXT
);

CREATE TABLE IF NOT EXISTS logs.fact_scheduler_event (
  source_doc_id TEXT PRIMARY KEY REFERENCES logs.fact_log_event(source_doc_id) ON DELETE CASCADE,
  worker_id INTEGER,
  criterion TEXT,
  controller_name TEXT,
  method_name TEXT,
  method_display_name TEXT,
  service_domain TEXT
);

CREATE TABLE IF NOT EXISTS logs.fact_error_event (
  source_doc_id TEXT PRIMARY KEY REFERENCES logs.fact_log_event(source_doc_id) ON DELETE CASCADE,
  error_message TEXT,
  exception_class TEXT,
  root_exception_class TEXT,
  error_keyword TEXT,
  caused_by_count INTEGER,
  stack_trace TEXT
);

CREATE TABLE IF NOT EXISTS logs.etl_watermark (
  pipeline_name TEXT PRIMARY KEY,
  last_event_timestamp TIMESTAMPTZ NOT NULL,
  last_source_doc_id TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
