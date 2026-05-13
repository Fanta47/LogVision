import hashlib
import pandas as pd

WINDOW_SIZE = 20
STEP_SIZE = 5

try:
    df = pd.read_csv('data/events_normalized.csv')
except Exception as e:
    raise SystemExit(f'Error read data/events_normalized.csv: {e}')

df['event_timestamp'] = pd.to_datetime(df['event_timestamp'], errors='coerce')
df = df.dropna(subset=['event_timestamp']).copy()

rows = []
for (app, comp), g in df.groupby(['application_key', 'component_name'], dropna=False):
    g = g.sort_values('event_timestamp')
    n = len(g)
    for i in range(0, max(1, n - WINDOW_SIZE + 1), STEP_SIZE):
        w = g.iloc[i:i+WINDOW_SIZE]
        if len(w) == 0:
            continue
        event_ids = w['id'].astype(str).tolist()
        sequence_text = ' [SEP] '.join(w['ml_text'].fillna('').astype(str).tolist())
        start_ts = w['event_timestamp'].iloc[0]
        end_ts = w['event_timestamp'].iloc[-1]
        uid = hashlib.sha256(f"{app}|{comp}|{start_ts}|{end_ts}|{'|'.join(event_ids)}".encode()).hexdigest()
        rows.append({
            'sequence_uid': uid,
            'application_key': app,
            'component_name': comp,
            'start_timestamp': start_ts,
            'end_timestamp': end_ts,
            'event_ids': '|'.join(event_ids),
            'sequence_text': sequence_text,
            'error_count': int((w['log_level'].astype(str).str.lower() == 'error').sum()),
            'warning_count': int((w['log_level'].astype(str).str.lower().isin(['warn', 'warning'])).sum()),
            'sla_not_found_count': int((w['event_type'].astype(str) == 'sla_lookup').sum() and (w.get('details', pd.Series(['']*len(w))).astype(str).str.contains('NOT FOUND', case=False, na=False).sum())),
            'sql_query_count': int((w['event_type'].astype(str) == 'sql_query').sum()),
            'unique_event_type_count': int(w['event_type'].nunique()),
            'duration_ms': int((end_ts - start_ts).total_seconds() * 1000),
        })

out = pd.DataFrame(rows)
out.to_csv('data/sequences.csv', index=False)
print(f'Sequences built: {len(out)} -> data/sequences.csv')
