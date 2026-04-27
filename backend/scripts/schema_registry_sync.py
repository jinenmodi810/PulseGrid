from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict

import requests

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "app" / "domain" / "avro_schemas"
DEFAULT_REGISTRY_URL = "http://localhost:18081"


def _subject_for_file(path: Path) -> str:
    event_type = path.stem
    return f"pulsegrid.{event_type}-value"


def _load_schema(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _register_schema(registry_url: str, subject: str, schema_text: str) -> Dict[str, object]:
    url = f"{registry_url.rstrip('/')}/subjects/{subject}/versions"
    body = {"schemaType": "AVRO", "schema": schema_text}
    response = requests.post(url, json=body, timeout=20)
    response.raise_for_status()
    return response.json()


def sync_schemas(registry_url: str) -> int:
    if not SCHEMA_DIR.exists():
        print(f"[error] schema directory missing: {SCHEMA_DIR}")
        return 1

    files = sorted(SCHEMA_DIR.glob("*.avsc"))
    if not files:
        print("[warn] no .avsc files found")
        return 0

    print(f"[info] syncing {len(files)} schemas -> {registry_url}")
    for path in files:
        subject = _subject_for_file(path)
        schema_text = _load_schema(path)
        result = _register_schema(registry_url, subject, schema_text)
        print(json.dumps({"subject": subject, "result": result}, ensure_ascii=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Register Avro event schemas in Schema Registry.")
    parser.add_argument("--registry-url", default=DEFAULT_REGISTRY_URL, help="Schema Registry base URL")
    args = parser.parse_args()
    return sync_schemas(args.registry_url)


if __name__ == "__main__":
    raise SystemExit(main())
