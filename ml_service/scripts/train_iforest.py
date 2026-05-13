import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer


def minmax(x):
    x = np.array(x, dtype=float)
    if len(x) == 0:
        return x
    mn, mx = x.min(), x.max()
    if mx == mn:
        return np.zeros_like(x)
    return (x - mn) / (mx - mn)

try:
    df = pd.read_csv('data/sequences.csv')
except Exception as e:
    raise SystemExit(f'Error read data/sequences.csv: {e}')

vec = TfidfVectorizer(max_features=5000)
X = vec.fit_transform(df['sequence_text'].fillna(''))
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)
raw = -model.score_samples(X)
score = minmax(raw)

out = df[['sequence_uid', 'application_key', 'component_name', 'start_timestamp', 'end_timestamp', 'event_ids']].copy()
out['iforest_anomaly_score'] = score.clip(0, 1)
out.to_csv('outputs/iforest_scores.csv', index=False)
joblib.dump({'vectorizer': vec, 'model': model}, 'models/iforest_tfidf.joblib')
print('Saved models/iforest_tfidf.joblib and outputs/iforest_scores.csv')
