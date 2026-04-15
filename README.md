📊 LogVision – Log Analysis & Intelligent Monitoring Platform
🚀 Overview

LogVision is an end-to-end log processing and analysis platform designed to automatically ingest, parse, structure, store, and analyze application logs using the ELK stack (Elasticsearch, Logstash, Kibana) and PostgreSQL, with an integrated Machine Learning layer for anomaly detection and predictive insights.

The platform transforms raw logs into structured datasets, enabling advanced monitoring, incident detection, and predictive analytics.

🧠 Architecture
Log Files → Logstash → Elasticsearch → ETL Service → PostgreSQL → ML Service → Predictions
🔹 Components
Logstash
Reads log files from a directory
Handles multiline logs
Parses multiple log formats
Categorizes logs using log_family and event_type
Elasticsearch
Stores structured log data
Acts as a buffer and validation layer
Kibana
Visualizes logs
Enables debugging and analysis
PostgreSQL
Stores structured datasets by category
Main data source for ML and application layer
ETL Service (Python)
Automatically extracts data from Elasticsearch
Inserts data into PostgreSQL
Runs continuously (no manual execution)
ML Service
Reads structured data from PostgreSQL
Performs anomaly detection and predictions
📂 Log Categories
🔹 SQL Dataset (sql_persistence)
SQL queries (SELECT, UPDATE, etc.)
Query stages (before/after parameters)
Result size, update count
Data source
🔹 Scheduler / Controller Dataset (scheduler_controller)
Controller name
Method name
Worker threads
Job criteria
🔹 Error Dataset (application_error)
Error messages
Exception classes
Root causes
Stack traces
🔹 Base Dataset (base_event)
Common fields across all logs
Timestamp, level, source, context
🗄️ Database Schema

The platform stores structured data into multiple tables:

base_event
sql_event
scheduler_controller_event
error_event

This separation ensures clean datasets and better ML performance.

⚙️ Features
Automatic log ingestion
Multiline log reconstruction
Multi-format parsing (SQL, errors, scheduler logs)
Dynamic log classification
Structured data extraction
Automated data export to PostgreSQL
Dataset separation by category
ML-ready data pipeline
Scalable architecture
🤖 Machine Learning Capabilities

LogVision enables:

Anomaly detection (error spikes, abnormal activity)
Time-series analysis
Incident prediction
Log clustering
Pattern recognition
📁 Project Structure
ELK/
├── docker-compose.yml
├── logstash/
│   └── pipeline/
│       └── logstash.conf
├── uploads/
│   └── raw/
├── etl/
│   └── export_to_postgres.py
├── ml/
│   └── model.py
└── README.md
🛠️ Setup Instructions
1. Start ELK Stack
docker-compose up -d
2. Upload Log Files

Place your logs in:

uploads/raw/
3. Log Processing

Logstash automatically:

Reads new files
Parses logs
Sends structured data to Elasticsearch
4. ETL Execution

The ETL service:

Reads from Elasticsearch
Inserts into PostgreSQL
Runs automatically
5. ML Processing

The ML service:

Reads PostgreSQL tables
Generates predictions
🔄 Automation Workflow
Drop log file
Logstash parses logs
Elasticsearch stores structured data
ETL service transfers data to PostgreSQL
ML service processes data and generates insights
🎯 Objectives
Centralize log management
Automate data processing
Enable intelligent monitoring
Prepare structured datasets for ML
Detect anomalies and predict failures
📌 Future Improvements
Real-time streaming (Kafka integration)
Advanced ML models (LSTM, anomaly detection)
Prediction dashboards
Alerting system
API integration
👨‍💻 Author

Fanta – LogVision Project

📜 License

This project is for academic and research purposes.

⭐ Notes

LogVision is designed as a scalable platform that bridges log management and intelligent analytics.
