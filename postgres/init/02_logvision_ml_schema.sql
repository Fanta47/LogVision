CREATE TABLE IF NOT EXISTS log_upload (
  id BIGSERIAL PRIMARY KEY,
  upload_uid VARCHAR(128) UNIQUE NOT NULL,
  original_file_name VARCHAR(255) NOT NULL,
  stored_file_name VARCHAR(255) NOT NULL,
  stored_path TEXT NOT NULL,
  application_key VARCHAR(100) NOT NULL,
  component_name VARCHAR(150) NOT NULL,
  uploaded_by VARCHAR(150),
  uploaded_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(50) DEFAULT 'uploaded',
  total_lines INT,
  parsed_events INT,
  failed_events INT,
  error_message TEXT
);

ALTER TABLE base_event ADD COLUMN IF NOT EXISTS id BIGSERIAL;
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS event_uid VARCHAR(128);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS es_id VARCHAR(256);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS upload_uid VARCHAR(128);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS upload_id BIGINT;
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS application_key VARCHAR(100);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS component_name VARCHAR(150);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS platform VARCHAR(120);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS environment VARCHAR(120);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS scope VARCHAR(120);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS thread_name VARCHAR(255);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS normalized_details TEXT;
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS template_id VARCHAR(128);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS details_hash VARCHAR(128);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS source_path TEXT;
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS stored_file_name VARCHAR(255);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS original_file_name VARCHAR(255);
ALTER TABLE base_event ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();

CREATE UNIQUE INDEX IF NOT EXISTS ux_base_event_event_uid ON base_event(event_uid);
CREATE INDEX IF NOT EXISTS idx_base_event_sequence ON base_event(application_key, component_name, event_timestamp);
CREATE INDEX IF NOT EXISTS idx_base_event_family_time ON base_event(log_family, event_timestamp);
CREATE INDEX IF NOT EXISTS idx_base_event_type_time ON base_event(event_type, event_timestamp);

CREATE TABLE IF NOT EXISTS sla_event (
  base_event_id BIGINT PRIMARY KEY,
  caller_class TEXT,
  caller_method TEXT,
  caller_line INT,
  sla_class_name TEXT,
  context_raw TEXT,
  sla_status VARCHAR(32),
  sla_result_pk TEXT
);

ALTER TABLE sql_event ADD COLUMN IF NOT EXISTS base_event_id BIGINT;
ALTER TABLE sql_event ADD COLUMN IF NOT EXISTS sql_query TEXT;
ALTER TABLE sql_event ADD COLUMN IF NOT EXISTS normalized_sql_query TEXT;
ALTER TABLE sql_event ADD COLUMN IF NOT EXISTS table_name TEXT;
ALTER TABLE sql_event ADD COLUMN IF NOT EXISTS query_length INT;
ALTER TABLE sql_event ADD COLUMN IF NOT EXISTS estimated_complexity_score NUMERIC(10,4);

CREATE TABLE IF NOT EXISTS etl_watermark (
  pipeline_name VARCHAR(128) PRIMARY KEY,
  last_event_timestamp TIMESTAMPTZ NOT NULL DEFAULT '1970-01-01 00:00:00+00',
  last_source_doc_id TEXT NOT NULL DEFAULT '',
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ml_log_sequence (
  id BIGSERIAL PRIMARY KEY,
  sequence_uid VARCHAR(128) UNIQUE NOT NULL,
  application_key VARCHAR(100) NOT NULL,
  component_name VARCHAR(150) NOT NULL,
  start_timestamp TIMESTAMPTZ,
  end_timestamp TIMESTAMPTZ,
  event_ids TEXT NOT NULL,
  error_count INT DEFAULT 0,
  warning_count INT DEFAULT 0,
  sla_not_found_count INT DEFAULT 0,
  sql_query_count INT DEFAULT 0,
  unique_event_type_count INT DEFAULT 0,
  duration_ms BIGINT DEFAULT 0,
  final_anomaly_score NUMERIC(10,6),
  final_anomaly_label VARCHAR(32),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ml_event_score (
  id BIGSERIAL PRIMARY KEY,
  base_event_id BIGINT,
  event_uid VARCHAR(128),
  sequence_uid VARCHAR(128),
  model_name VARCHAR(120) NOT NULL,
  model_version VARCHAR(60) NOT NULL,
  anomaly_score NUMERIC(10,6) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ml_model_registry (
  id BIGSERIAL PRIMARY KEY,
  model_name VARCHAR(120) NOT NULL,
  model_version VARCHAR(60) NOT NULL,
  model_type VARCHAR(120),
  artifact_path TEXT,
  metrics_json TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE(model_name, model_version)
);
