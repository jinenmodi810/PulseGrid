from __future__ import annotations

import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = REPO_ROOT / "backend" / "docs" / "project_file_inventory.md"


def _git_lines(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _classify(path: str) -> str:
    p = path.lower()
    if p.startswith("backend/app/api/"):
        return "Backend API routes/dependencies"
    if p.startswith("backend/app/services/"):
        return "Backend domain/service logic"
    if p.startswith("backend/app/jobs/"):
        return "Data pipeline jobs (outbox/bronze/silver/gold)"
    if p.startswith("backend/app/domain/"):
        return "Event/domain contracts"
    if p.startswith("backend/app/observability/"):
        return "Observability and lineage"
    if p.startswith("backend/app/db/"):
        return "Database models/queries/session"
    if p.startswith("backend/app/models/") or p.startswith("backend/app/schemas/"):
        return "Data models and schemas"
    if p.startswith("backend/tests/"):
        return "Tests"
    if p.startswith("backend/scripts/"):
        return "Operational scripts"
    if p.startswith("backend/docs/"):
        return "Architecture/docs/runbooks"
    if p.startswith("backend/orchestration/"):
        return "Orchestration (Dagster)"
    if p.startswith("backend/dbt_project/"):
        return "Analytics engineering (dbt)"
    if p.startswith("lib/"):
        return "Flutter app"
    if p.startswith("android/") or p.startswith("ios/") or p.startswith("macos/") or p.startswith("linux/") or p.startswith("windows/") or p.startswith("web/"):
        return "Platform/mobile runtime files"
    if p.startswith("assets/"):
        return "Static assets"
    if p in {"docker-compose.yml", "makefile", "pubspec.yaml", "pubspec.lock"}:
        return "Project infra/config entrypoints"
    if p.endswith(".lock") or "generated" in p:
        return "Generated/build metadata"
    return "Other repository files"


def main() -> int:
    tracked = _git_lines(["ls-files"])
    untracked = _git_lines(["ls-files", "--others", "--exclude-standard"])
    all_paths = sorted(set(tracked + untracked))

    groups: dict[str, list[str]] = defaultdict(list)
    for path in all_paths:
        groups[_classify(path)].append(path)

    lines: list[str] = []
    lines.append("# PulseGrid File Inventory")
    lines.append("")
    lines.append(f"- Generated at: `{datetime.now(tz=timezone.utc).isoformat()}`")
    lines.append(f"- Total files inventoried: `{len(all_paths)}`")
    lines.append("- Source: `git ls-files` + untracked non-ignored files")
    lines.append("")
    lines.append("Use this as your learning map: start with backend API/services/jobs/docs, then Flutter integration.")
    lines.append("")

    for group_name in sorted(groups.keys()):
        lines.append(f"## {group_name}")
        lines.append("")
        for path in groups[group_name]:
            lines.append(f"- `{path}`")
        lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"[ok] wrote inventory: {OUT_PATH}")
    print(f"[ok] files: {len(all_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
