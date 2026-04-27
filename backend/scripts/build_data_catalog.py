from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

LINEAGE_FILE = Path(__file__).resolve().parents[1] / "data" / "lineage" / "events.jsonl"
OUT_FILE = Path(__file__).resolve().parents[1] / "docs" / "data-platform" / "data_catalog.md"


def main() -> int:
    if not LINEAGE_FILE.exists():
        print(f"[warn] no lineage file at {LINEAGE_FILE}")
        return 1

    jobs: dict[str, dict[str, set[str]]] = defaultdict(lambda: {"inputs": set(), "outputs": set()})
    lines = LINEAGE_FILE.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if not line.strip():
            continue
        payload = json.loads(line)
        job = str(payload.get("job_name") or "unknown")
        for i in payload.get("inputs") or []:
            jobs[job]["inputs"].add(str(i))
        for o in payload.get("outputs") or []:
            jobs[job]["outputs"].add(str(o))

    out = ["# PulseGrid Data Catalog", "", "Auto-generated from lineage events.", ""]
    for job_name in sorted(jobs.keys()):
        out.append(f"## {job_name}")
        out.append("")
        out.append("### Inputs")
        for value in sorted(jobs[job_name]["inputs"]):
            out.append(f"- `{value}`")
        out.append("")
        out.append("### Outputs")
        for value in sorted(jobs[job_name]["outputs"]):
            out.append(f"- `{value}`")
        out.append("")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")
    print(f"[ok] wrote catalog -> {OUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
