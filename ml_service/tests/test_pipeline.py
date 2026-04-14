from pathlib import Path

import numpy as np

from app.preprocess import run_preprocess


def test_preprocess_creates_sequences(tmp_path: Path):
    out_dir = tmp_path / "processed"
    out_dir.mkdir()
    # use sample CSV from package
    sample_csv = Path(__file__).parents[1] / "data" / "raw_sample" / "sample_logs.csv"
    seq_path = run_preprocess(csv_fallback=str(sample_csv), out_dir=str(out_dir), seq_len=2)
    arr = np.load(seq_path)
    assert arr.ndim == 3
