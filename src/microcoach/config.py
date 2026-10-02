from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    refresh_seconds: float = float(os.getenv("MICROCOACH_REFRESH_SECONDS", "1"))
    baselines_path: str = os.getenv("MICROCOACH_BASELINES_PATH", "data/baselines.json")
