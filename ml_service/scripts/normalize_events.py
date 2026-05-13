import re
import pandas as pd

DATE_RE = re.compile(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b')
IP_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
NUM_RE = re.compile(r'\b\d+\b')
PATH_RE = re.compile(r'([A-Za-z]:\\[^\s]+|/[^\s]+)')
HEX_RE = re.compile(r'\b[a-fA-F0-9]{12,}\b')
SPACE_RE = re.compile(r'\s+')

def normalize(t):
    if not isinstance(t, str):
        return ''
    t = DATE_RE.sub('<DATE>', t)
    t = IP_RE.sub('<IP>', t)
    t = PATH_RE.sub('<PATH>', t)
    t = HEX_RE.sub('<HEX>', t)
    t = NUM_RE.sub('<NUM>', t)
    return SPACE_RE.sub(' ', t).strip()

try:
    df = pd.read_csv('data/events.csv')
except Exception as e:
    raise SystemExit(f'Error read data/events.csv: {e}')

if 'normalized_details' not in df.columns:
    df['normalized_details'] = ''

df['normalized_details'] = df.apply(lambda r: r['normalized_details'] if isinstance(r['normalized_details'], str) and r['normalized_details'].strip() else normalize(r.get('details', '')), axis=1)

df['ml_text'] = df.apply(lambda r: f"app={r.get('application_key','')} component={r.get('component_name','')} family={r.get('log_family','')} type={r.get('event_type','')} level={r.get('log_level','')} thread={r.get('thread_name','')} message={r.get('normalized_details','')}", axis=1)

df.to_csv('data/events_normalized.csv', index=False)
print(f'Normalized: {len(df)} rows -> data/events_normalized.csv')
