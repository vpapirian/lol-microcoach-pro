from __future__ import annotations
import base64
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

def _read_lockfile(lockfile_path: Path) -> Optional[Tuple[str, str, str, str, str]]:
    # lockfile format: name:pid:port:password:protocol
    try:
        raw = lockfile_path.read_text(encoding="utf-8").strip()
        parts = raw.split(":")
        if len(parts) != 5:
            return None
        return tuple(parts)  # type: ignore
    except Exception:
        return None

def find_lockfile() -> Optional[Path]:
    # Common default location for Windows LoL client lockfile:
    # C:\Riot Games\League of Legends\lockfile
    candidates = []
    env = os.getenv("LOCALAPPDATA")
    if env:
        # Many installs keep lockfile under the LoL install folder, not LOCALAPPDATA,
        # but we keep this as a hint for custom setups.
        candidates.append(Path(env) / "Riot Games" / "League of Legends" / "lockfile")

    candidates += [
        Path("C:/Riot Games/League of Legends/lockfile"),
        Path("C:/Program Files/Riot Games/League of Legends/lockfile"),
        Path("C:/Program Files (x86)/Riot Games/League of Legends/lockfile"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def get_lcu_session(lockfile: Optional[Path] = None) -> Optional[requests.Session]:
    lf = lockfile or find_lockfile()
    if not lf:
        return None
    data = _read_lockfile(lf)
    if not data:
        return None
    name, pid, port, password, protocol = data
    token = base64.b64encode(f"riot:{password}".encode("utf-8")).decode("utf-8")

    s = requests.Session()
    s.verify = False
    s.headers.update({"Authorization": f"Basic {token}"})
    s._microcoach_base = f"{protocol}://127.0.0.1:{port}"  # type: ignore[attr-defined]
    return s

def get(s: requests.Session, path: str, timeout: float = 0.5) -> Optional[Dict[str, Any]]:
    base = getattr(s, "_microcoach_base", None)
    if not base:
        return None
    try:
        r = s.get(f"{base}{path}", timeout=timeout)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None
