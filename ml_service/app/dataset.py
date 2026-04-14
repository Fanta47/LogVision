from __future__ import annotations

from typing import Optional

import numpy as np
import torch
from torch.utils.data import Dataset


class SequenceDataset(Dataset):
    def __init__(self, sequences_path: str):
        self.sequences = np.load(sequences_path)

    def __len__(self) -> int:
        return int(self.sequences.shape[0])

    def __getitem__(self, idx: int) -> torch.Tensor:
        arr = self.sequences[idx]
        return torch.from_numpy(arr)
