from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))


@dataclass
class Settings:
    PG_HOST: str = os.getenv("PG_HOST", "localhost")
    PG_PORT: int = int(os.getenv("PG_PORT", 5432))
    PG_DB: str = os.getenv("PG_DB", "logs")
    PG_USER: str = os.getenv("PG_USER", "logs_user")
    PG_PASSWORD: str = os.getenv("PG_PASSWORD", "logs_pass")
    MODEL_DIR: str = os.getenv("MODEL_DIR", "./data/checkpoints")
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./data/outputs")
    DEVICE: str = os.getenv("DEVICE", "cpu")


settings = Settings()
