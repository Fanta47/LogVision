CREATE TABLE IF NOT EXISTS base_event (
  source_doc_id TEXT PRIMARY KEY,
  event_timestamp TIMESTAMPTZ NOT NULL,
  application_name TEXT NOT NULL,
  application_key TEXT NOT NULL,
  application_group TEXT NOT NULL,
  log_level TEXT,
  log_origin TEXT,
  thread TEXT,
  log_family TEXT NOT NULL,
  event_type TEXT NOT NULL,
  parse_status TEXT NOT NULL,
  parse_confidence TEXT NOT NULL,
  analysis_status TEXT,
  source_file TEXT,
  context TEXT,
  details TEXT,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_base_event_ts ON base_event(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_base_event_app_ts ON base_event(application_key, event_timestamp);
CREATE INDEX IF NOT EXISTS idx_base_event_family_event ON base_event(log_family, event_type);

CREATE TABLE IF NOT EXISTS sql_event (
  source_doc_id TEXT PRIMARY KEY REFERENCES base_event(source_doc_id) ON DELETE CASCADE,
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

CREATE TABLE IF NOT EXISTS scheduler_controller_event (
  source_doc_id TEXT PRIMARY KEY REFERENCES base_event(source_doc_id) ON DELETE CASCADE,
  worker_id INTEGER,
  criterion TEXT,
  controller_name TEXT,
  method_name TEXT,
  method_display_name TEXT,
  service_domain TEXT
);

CREATE TABLE IF NOT EXISTS error_event (
  source_doc_id TEXT PRIMARY KEY REFERENCES base_event(source_doc_id) ON DELETE CASCADE,
  error_message TEXT,
  exception_class TEXT,
  root_exception_class TEXT,
  error_keyword TEXT,
  caused_by_count INTEGER,
  stack_trace TEXT
);

CREATE TABLE IF NOT EXISTS etl_checkpoint (
  pipeline_name TEXT PRIMARY KEY,
  last_event_timestamp TIMESTAMPTZ NOT NULL,
  last_source_doc_id TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
