from __future__ import annotations

import argparse
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

OUT_REPORT = Path(__file__).resolve().parents[1] / "docs" / "data-platform" / "performance_benchmark_report.md"


def _latencies(base_url: str, endpoint: str, n: int) -> list[float]:
    values: list[float] = []
    for _ in range(n):
        start = time.perf_counter()
        response = requests.get(f"{base_url.rstrip('/')}{endpoint}", timeout=20)
        response.raise_for_status()
        values.append((time.perf_counter() - start) * 1000.0)
    return values


def _render(latencies: dict[str, list[float]], sample_size: int) -> str:
    lines = [
        "# PulseGrid Performance Benchmark Report",
        "",
        f"- Generated at: `{datetime.now(tz=timezone.utc).isoformat()}`",
        f"- Sample size per endpoint: `{sample_size}`",
        "",
        "## Analytics API Latency (ms)",
        "",
    ]
    for endpoint, vals in latencies.items():
        p95 = sorted(vals)[max(0, int(len(vals) * 0.95) - 1)]
        lines.append(f"### `{endpoint}`")
        lines.append(f"- avg_ms: `{statistics.mean(vals):.2f}`")
        lines.append(f"- p95_ms: `{p95:.2f}`")
        lines.append(f"- max_ms: `{max(vals):.2f}`")
        lines.append(f"- throughput_rps_est: `{(1000.0 / statistics.mean(vals)):.2f}`")
        lines.append("")
    lines.extend(
        [
            "## Cost Notes (Local Dev Proxy)",
            "",
            "- Compute: single local machine + Docker services.",
            "- Storage: MinIO object storage footprint scales with Bronze/Silver/Gold retention.",
            "- Network: local-only in dev; production cost model should add broker egress and object-store requests.",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark PulseGrid analytics endpoints.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8002")
    parser.add_argument("--samples", type=int, default=20)
    args = parser.parse_args()

    endpoints = [
        "/analytics/overview",
        "/analytics/incidents-by-zone",
        "/analytics/time-to-response",
    ]
    results = {ep: _latencies(args.base_url, ep, args.samples) for ep in endpoints}
    report = _render(results, args.samples)
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(f"[ok] report generated: {OUT_REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
