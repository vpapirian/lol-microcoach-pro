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

def _to_int(value: Any, default: int = 0) -> int:
    """Coerce an API value to int, falling back to default for None or junk."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if math.isfinite(result) else default


_NAME_KEYS = ("riotId", "summonerName", "riotIdGameName")


def _find_active_player_entry(allgamedata: Dict[str, Any], active: Dict[str, Any]) -> Dict[str, Any]:
    """Return the allPlayers entry for the active player, or {} if not found.

    The Live Client API reports scores (kills, deaths, assists, creepScore) and
    the champion name on the allPlayers entries, not on activePlayer.
    """
    players = allgamedata.get("allPlayers")
    if not isinstance(players, list):
        return {}
    names = {str(active[k]) for k in _NAME_KEYS if active.get(k)}
    if not names:
        return {}
    for player in players:
        if isinstance(player, dict) and any(str(player.get(k)) in names for k in _NAME_KEYS if player.get(k)):
            return player
    return {}


def compute_snapshot(allgamedata: Dict[str, Any], summoner_name_hint: Optional[str] = None) -> Optional[Snapshot]:
    if not isinstance(allgamedata, dict):
        return None
    # Pick "activePlayer" as the user
    active = allgamedata.get("activePlayer")
    if not isinstance(active, dict):
        return None

    me = _find_active_player_entry(allgamedata, active)

    game_time = _to_float(_safe_get(allgamedata, "gameData", "gameTime", default=0.0))
    champ = str(me.get("championName") or _safe_get(active, "championStats", "name", default="") or "")
    level = _to_int(_safe_get(active, "level", default=0))
    gold = _to_int(_safe_get(active, "currentGold", default=0))

    # Total gold isn't always directly available; estimate with current + some earned (fallback)
    total_gold = _to_int(_safe_get(active, "totalGold", default=gold), default=gold)

    scores = me.get("scores") or _safe_get(active, "scores", default={}) or {}
    if not isinstance(scores, dict):
        scores = {}
    kills = _to_int(scores.get("kills", 0))
    deaths = _to_int(scores.get("deaths", 0))
    assists = _to_int(scores.get("assists", 0))
    cs = _to_int(scores.get("creepScore", 0))

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
