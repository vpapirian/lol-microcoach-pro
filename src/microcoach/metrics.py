from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
import math

@dataclass(frozen=True)
class Snapshot:
    game_time: float
    champion_name: str
    level: int
    kills: int
    deaths: int
    assists: int
    current_gold: int
    total_gold: int
    cs: int
    cs_per_min: float
    movement_score: float

def _safe_get(d: Dict[str, Any], *keys, default=None):
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def compute_snapshot(allgamedata: Dict[str, Any], summoner_name_hint: Optional[str] = None) -> Optional[Snapshot]:
    # Pick "activePlayer" as the user
    active = allgamedata.get("activePlayer")
    if not isinstance(active, dict):
        return None

    game_time = float(_safe_get(allgamedata, "gameData", "gameTime", default=0.0) or 0.0)
    champ = str(_safe_get(active, "championStats", "name", default="") or "")
    level = int(_safe_get(active, "level", default=0) or 0)
    gold = int(_safe_get(active, "currentGold", default=0) or 0)

    # Total gold isn't always directly available; estimate with current + some earned (fallback)
    total_gold = int(_safe_get(active, "totalGold", default=gold) or gold)

    scores = _safe_get(active, "scores", default={}) or {}
    kills = int(scores.get("kills", 0) or 0)
    deaths = int(scores.get("deaths", 0) or 0)
    assists = int(scores.get("assists", 0) or 0)
    cs = int(scores.get("creepScore", 0) or 0)

    minutes = max(game_time / 60.0, 1e-6)
    cspm = cs / minutes

    # Demo "movement_score": combines cspm, KDA, and time (placeholder until you plug real mouse/pathing data)
    kda = (kills + assists) / max(deaths, 1)
    movement_score = (cspm * 10.0) + (kda * 8.0) + (math.log1p(minutes) * 3.5)

    return Snapshot(
        game_time=game_time,
        champion_name=champ or "Unknown",
        level=level,
        kills=kills,
        deaths=deaths,
        assists=assists,
        current_gold=gold,
        total_gold=total_gold,
        cs=cs,
        cs_per_min=float(cspm),
        movement_score=float(movement_score),
    )
