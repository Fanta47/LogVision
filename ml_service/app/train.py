from __future__ import annotations

import argparse
import os
from typing import Tuple

import torch
from torch import nn, optim
from torch.utils.data import DataLoader

from .config import settings
from .dataset import SequenceDataset
from .model import LogBERTLike
from .utils import ensure_dir, set_seed


def train_loop(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer: optim.Optimizer,
    device: str,
    epochs: int = 1,
):
    criterion = nn.MSELoss()
    model.to(device)
    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch in dataloader:
            batch = batch.to(device)
            # model returns a single vector per sequence; compare to mean vector
            target = batch.mean(dim=1)
            optimizer.zero_grad()
            out = model(batch)
            loss = criterion(out, target)
            loss.backward()
            optimizer.step()
            total_loss += float(loss.item())
        print(f"Epoch {epoch+1}/{epochs} loss={total_loss/len(dataloader):.6f}")


def main(args: argparse.Namespace) -> Tuple[str, str]:
    set_seed()
    processed_dir = os.path.join(os.getcwd(), "data", "processed")
    ensure_dir(processed_dir)
    seq_path = os.path.join(processed_dir, "sequences.npy")
    if not os.path.exists(seq_path):
        raise SystemExit("No processed sequences found. Run preprocess first or provide sample data.")

    dataset = SequenceDataset(seq_path)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    # infer dims
    sample = dataset[0]
    seq_len, feat_dim = sample.shape

    model = LogBERTLike(feature_dim=feat_dim)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    train_loop(model, dataloader, optimizer, device=settings.DEVICE, epochs=args.epochs)

    ensure_dir(settings.MODEL_DIR)
    ckpt_path = os.path.join(settings.MODEL_DIR, "latest.pt")
    torch.save({"model_state_dict": model.state_dict()}, ckpt_path)
    print("Saved checkpoint to", ckpt_path)
    return ckpt_path, seq_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()
    main(args)
