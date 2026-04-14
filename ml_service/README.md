# ml_service

Service for log anomaly detection (LogBERT-inspired skeleton).

Quick start

- Create a Python 3.11 virtualenv:

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

- Example commands (from `ml_service/`):

```bash
# Preprocess data (reads from PG if available, otherwise uses sample CSV)
python -m app.preprocess

# Train a small model
python -m app.train --epochs 2 --batch-size 8

# Run inference
python -m app.infer --checkpoint ./data/checkpoints/latest.pt
```

Structure

- `app/` : core modules (preprocess, dataset, model, train, infer)
- `data/` : `raw_sample/`, `processed/`, `checkpoints/`, `outputs/`
- `notebooks/` : experiments
- `tests/` : basic pipeline tests

See in-file docstrings for more details.
