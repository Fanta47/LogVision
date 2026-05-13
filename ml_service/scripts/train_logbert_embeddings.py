import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.ensemble import IsolationForest
from transformers import AutoModel, AutoTokenizer

MODEL_NAME = 'distilbert-base-uncased'


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

texts = df['sequence_text'].fillna('').astype(str).tolist()
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using device: {device}')

tok = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME).to(device)
model.eval()

embeds = []
with torch.no_grad():
    for t in texts:
        inp = tok(t, truncation=True, padding='max_length', max_length=512, return_tensors='pt')
        inp = {k: v.to(device) for k, v in inp.items()}
        out = model(**inp)
        cls = out.last_hidden_state[:, 0, :].squeeze(0).cpu().numpy()
        embeds.append(cls)

E = np.vstack(embeds) if embeds else np.zeros((0, 768))
iso = IsolationForest(contamination=0.05, random_state=42)
if len(E) > 0:
    iso.fit(E)
    raw = -iso.score_samples(E)
    score = minmax(raw).clip(0, 1)
else:
    score = np.array([])

np.save('models/logbert_embeddings.npy', E)
joblib.dump({'model_name': MODEL_NAME, 'iforest': iso}, 'models/logbert_like_iforest.joblib')

out = df[['sequence_uid', 'application_key', 'component_name', 'start_timestamp', 'end_timestamp', 'event_ids']].copy()
out['logbert_like_score'] = score
out.to_csv('outputs/logbert_like_scores.csv', index=False)
print('Saved LogBERT-like outputs and artifacts')
