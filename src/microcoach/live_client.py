from __future__ import annotations
import requests
from typing import Any, Dict, Optional

LIVE_BASE = "http://localhost:2999/liveclientdata"


def is_available(timeout: float = 0.15) -> bool:
    try:
        r = requests.get(f"{LIVE_BASE}/gamestats", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False

def get_all(timeout: float = 3.0, retries: int = 2):
    import time
    import requests

    url = f"{LIVE_BASE}/allgamedata"

    for attempt in range(retries + 1):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code != 200:
                return None
            return r.json()
        except Exception:
            time.sleep(0.25 * (attempt + 1))

    return None

