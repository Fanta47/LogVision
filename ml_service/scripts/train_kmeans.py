import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
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
km = KMeans(n_clusters=min(10, len(df)) if len(df) > 0 else 1, random_state=42, n_init='auto')
labels = km.fit_predict(X)
dist = km.transform(X)[np.arange(X.shape[0]), labels]
score = minmax(dist)

out = df[['sequence_uid', 'application_key', 'component_name', 'start_timestamp', 'end_timestamp', 'event_ids']].copy()
out['kmeans_anomaly_score'] = score.clip(0, 1)
out.to_csv('outputs/kmeans_scores.csv', index=False)
joblib.dump({'vectorizer': vec, 'model': km}, 'models/kmeans_tfidf.joblib')
print('Saved models/kmeans_tfidf.joblib and outputs/kmeans_scores.csv')
