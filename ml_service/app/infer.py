from __future__ import annotations

import argparse
import os
from typing import List

import numpy as np
import pandas as pd
import torch

from .config import settings
from .dataset import SequenceDataset
from .model import LogBERTLike
from .utils import ensure_dir


def infer(checkpoint: str, sequences_path: str) -> str:
    seqs = np.load(sequences_path)
    if seqs.shape[0] == 0:
        raise SystemExit("No sequences available for inference.")

    # get dims
    seq_len, feat_dim = seqs.shape[1], seqs.shape[2]
    model = LogBERTLike(feature_dim=feat_dim)
    ckpt = torch.load(checkpoint, map_location=settings.DEVICE)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()

    scores: List[float] = []
    with torch.no_grad():
        for seq in seqs:
            tensor = torch.from_numpy(seq).unsqueeze(0)
            out = model(tensor)
            target = tensor.mean(dim=1)
            mse = torch.mean((out - target) ** 2).item()
            scores.append(mse)

    ensure_dir(settings.OUTPUT_DIR)
    out_path = os.path.join(settings.OUTPUT_DIR, "inference_scores.csv")
    pd.DataFrame({"score": scores}).to_csv(out_path, index=False)
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--sequences", default="./data/processed/sequences.npy")
    args = parser.parse_args()
    out = infer(args.checkpoint, args.sequences)
    print("Saved inference output to", out)
