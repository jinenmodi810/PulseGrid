"""Lightweight lineage emitter for local cataloging and audits."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_log = logging.getLogger("pulsegrid.lineage")
_LINEAGE_FILE = Path(__file__).resolve().parents[2] / "data" / "lineage" / "events.jsonl"


def emit_lineage_event(
    *,
    job_name: str,
    status: str,
    inputs: list[str],
    outputs: list[str],
    run_stats: dict[str, Any] | None = None,
) -> None:
    """Append a structured lineage event to a local catalog file."""
    event = {
        "captured_at": datetime.now(tz=timezone.utc).isoformat(),
        "job_name": job_name,
        "status": status,
        "inputs": inputs,
        "outputs": outputs,
        "run_stats": run_stats or {},
    }
    _LINEAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with _LINEAGE_FILE.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(event, ensure_ascii=True) + "\n")
    _log.info(
        "lineage_event job=%s status=%s inputs=%s outputs=%s",
        job_name,
        status,
        len(inputs),
        len(outputs),
    )
