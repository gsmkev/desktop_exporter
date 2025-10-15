from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def _config_path() -> Path:
    # Store config in user's home directory
    home = Path(os.path.expanduser("~"))
    return home / ".desktop_exporter_config.json"


def load_config() -> Dict[str, Any]:
    path = _config_path()
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        # Corrupt or unreadable file; ignore and start fresh
        return {}


def save_config(config: Dict[str, Any]) -> None:
    path = _config_path()
    try:
        with path.open("w", encoding="utf-8") as fh:
            json.dump(config, fh, ensure_ascii=False, indent=2)
    except Exception:
        # Best-effort; ignore persistence errors
        pass

