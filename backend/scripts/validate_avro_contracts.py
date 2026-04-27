from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from typing import Any, Dict

from fastavro import parse_schema, schemaless_writer

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "app" / "domain" / "avro_schemas"


def _event_schema(event_type: str) -> Dict[str, Any]:
    path = SCHEMA_DIR / f"{event_type}.avsc"
    if not path.exists():
        raise FileNotFoundError(f"No schema for event_type='{event_type}' at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_envelope(envelope: Dict[str, Any]) -> None:
    event_type = envelope.get("event_type")
    if not isinstance(event_type, str) or not event_type:
        raise ValueError("event_type is required in envelope")

    schema = parse_schema(_event_schema(event_type))
    # Serialization fails when envelope violates Avro contract.
    schemaless_writer(io.BytesIO(), schema, envelope)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate event envelope against Avro schema.")
    parser.add_argument("--file", required=True, help="Path to JSON envelope file")
    args = parser.parse_args()

    data = json.loads(Path(args.file).read_text(encoding="utf-8"))
    validate_envelope(data)
    print(f"[ok] envelope valid for event_type={data.get('event_type')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
