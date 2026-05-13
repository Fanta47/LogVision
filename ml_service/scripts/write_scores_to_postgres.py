import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

host = os.getenv('POSTGRES_HOST', 'localhost')
port = os.getenv('POSTGRES_PORT', '5432')
db = os.getenv('POSTGRES_DB', 'logvision')
user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
url = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'

try:
    df = pd.read_csv('outputs/model_comparison.csv')
except Exception as e:
    raise SystemExit(f'Error reading outputs/model_comparison.csv: {e}')

engine = create_engine(url)
with engine.begin() as conn:
    for _, r in df.iterrows():
        conn.execute(text('''
            INSERT INTO ml_log_sequence(sequence_uid, application_key, component_name, start_timestamp, end_timestamp, event_ids, final_anomaly_score, final_anomaly_label, updated_at)
            VALUES (:sequence_uid, :application_key, :component_name, :start_timestamp, :end_timestamp, :event_ids, :final_anomaly_score, :final_anomaly_label, NOW())
            ON CONFLICT (sequence_uid) DO UPDATE SET
              final_anomaly_score=EXCLUDED.final_anomaly_score,
              final_anomaly_label=EXCLUDED.final_anomaly_label,
              updated_at=NOW()
        '''), r.to_dict())

        ids = [x for x in str(r['event_ids']).split('|') if x]
        for eid in ids:
            conn.execute(text('''
                INSERT INTO ml_event_score(base_event_id, sequence_uid, model_name, model_version, anomaly_score)
                VALUES (:base_event_id, :sequence_uid, 'ensemble_logbert_like', 'v1', :anomaly_score)
            '''), {'base_event_id': int(eid), 'sequence_uid': r['sequence_uid'], 'anomaly_score': float(r['final_anomaly_score'])})

print('Scores written to PostgreSQL')
