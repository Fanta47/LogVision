import pandas as pd

try:
    a = pd.read_csv('outputs/iforest_scores.csv')
    b = pd.read_csv('outputs/kmeans_scores.csv')
    c = pd.read_csv('outputs/logbert_like_scores.csv')
except Exception as e:
    raise SystemExit(f'Error reading score files: {e}')

df = a.merge(b, on=['sequence_uid','application_key','component_name','start_timestamp','end_timestamp','event_ids'])\
      .merge(c, on=['sequence_uid','application_key','component_name','start_timestamp','end_timestamp','event_ids'])

df['final_anomaly_score'] = (0.25 * df['iforest_anomaly_score'] + 0.25 * df['kmeans_anomaly_score'] + 0.50 * df['logbert_like_score']).clip(0, 1)

def label(x):
    if x < 0.30:
        return 'normal'
    if x < 0.70:
        return 'suspicious'
    return 'anomalous'

df['final_anomaly_label'] = df['final_anomaly_score'].apply(label)
df.to_csv('outputs/model_comparison.csv', index=False)
print('Saved outputs/model_comparison.csv')
