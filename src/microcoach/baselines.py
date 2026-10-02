from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

@dataclass(frozen=True)
class Baseline:
    mean: float
    std: float

def load_baselines(path: str) -> Dict[str, Dict[str, Baseline]]:
    p = Path(path)
    raw = json.loads(p.read_text(encoding="utf-8"))
    out: Dict[str, Dict[str, Baseline]] = {}
    for metric, tiers in raw.items():
        out[metric] = {}
        for tier, stats in tiers.items():
            out[metric][tier] = Baseline(mean=float(stats["mean"]), std=float(stats["std"]))
    return out
