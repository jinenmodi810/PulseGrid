"""Shared helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_array(path: Path) -> list[dict[str, Any]]:
    """Load a JSON array from disk; return empty list if missing or invalid."""
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        return []
    return [x for x in raw if isinstance(x, dict)]
