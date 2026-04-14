from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn


class LogBERTLike(nn.Module):
    """A small, extensible transformer-based encoder for sequences of TF-IDF vectors.

    Input shape: (batch, seq_len, feature_dim)
    """

    def __init__(self, feature_dim: int, d_model: int = 128, nhead: int = 4, num_layers: int = 2):
        super().__init__()
        self.input_proj = nn.Linear(feature_dim, d_model)
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.out = nn.Linear(d_model, feature_dim)  # reconstruct feature vector

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, feature_dim)
        h = self.input_proj(x)  # (batch, seq_len, d_model)
        h = self.encoder(h)
        # mean pooling over sequence
        h_mean = h.mean(dim=1)  # (batch, d_model)
        out = self.out(h_mean)  # (batch, feature_dim)
        return out
