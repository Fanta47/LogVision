from __future__ import annotations

import os
from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

from .config import settings
from .db import get_events_sample
from .utils import ensure_dir


def canonicalize_event(row: pd.Series) -> str:
    parts = []
    if pd.notna(row.get("level")):
        parts.append(f"[{row.level}]")
    msg = row.get("message") or ""
    parts.append(msg)
    host = row.get("host")
    if pd.notna(host):
        parts.append(f"host={host}")
    user = row.get("user")
    if pd.notna(user):
        parts.append(f"user={user}")
    return " ".join(parts)


def load_events_from_csv(path: str) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["timestamp"])  # basic


def build_sequences(df: pd.DataFrame, seq_len: int = 32) -> Tuple[np.ndarray, List[dict]]:
    # Prepare textual representation
    df = df.dropna(subset=["application_key", "timestamp"])
    df["text"] = df.apply(canonicalize_event, axis=1)

    # Group and sort
    groups = df.groupby("application_key")
    corpus = df["text"].tolist()

    vec = TfidfVectorizer(max_features=256)
    X_all = vec.fit_transform(corpus)
    feature_dim = X_all.shape[1]

    sequences = []
    metadata = []

    for app_key, g in groups:
        g_sorted = g.sort_values("timestamp")
        texts = g_sorted["text"].tolist()
        if len(texts) < seq_len:
            continue
        # transform texts for this group
        X = vec.transform(texts).toarray()
        # sliding windows
        for i in range(0, len(X) - seq_len + 1):
            seq = X[i : i + seq_len]
            sequences.append(seq.astype(np.float32))
            metadata.append({"application_key": app_key, "start_idx": int(i)})

    if len(sequences) == 0:
        return np.zeros((0, seq_len, feature_dim), dtype=np.float32), metadata

    return np.stack(sequences), metadata


def run_preprocess(
    csv_fallback: str | None = None, out_dir: str | None = None, seq_len: int = 32
) -> str:
    out_dir = out_dir or settings.MODEL_DIR.replace("checkpoints", "processed")
    ensure_dir(out_dir)
    try:
        df = get_events_sample()
    except Exception:
        if csv_fallback is None:
            csv_fallback = os.path.join(os.getcwd(), "data", "raw_sample", "sample_logs.csv")
        df = load_events_from_csv(csv_fallback)

    sequences, metadata = build_sequences(df, seq_len=seq_len)

    seq_path = os.path.join(out_dir, "sequences.npy")
    meta_path = os.path.join(out_dir, "metadata.csv")
    np.save(seq_path, sequences)
    pd.DataFrame(metadata).to_csv(meta_path, index=False)
    return seq_path


if __name__ == "__main__":
    out = run_preprocess()
    print("Saved sequences to", out)
