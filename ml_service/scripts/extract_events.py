import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('POSTGRES_HOST', 'localhost')
port = os.getenv('POSTGRES_PORT', '5432')
db = os.getenv('POSTGRES_DB', 'logvision')
user = os.getenv('POSTGRES_USER', 'postgres')
password = os.getenv('POSTGRES_PASSWORD', 'postgres')

os.makedirs('data', exist_ok=True)

url = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}'
query = '''
SELECT id, event_timestamp, application_key, component_name, log_family,
       event_type, log_level, thread_name, normalized_details, details
FROM base_event
ORDER BY application_key, component_name, event_timestamp
'''

try:
    engine = create_engine(url)
    df = pd.read_sql(query, engine)
    df.to_csv('data/events.csv', index=False)
    print(f'Export done: {len(df)} rows -> data/events.csv')
except Exception as e:
    raise SystemExit(f'Error export events: {e}')
