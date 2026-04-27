# Dagster Orchestration

This module orchestrates the existing PulseGrid pipeline jobs:

- `pulsegrid_hourly_pipeline`: outbox -> bronze -> silver -> gold
- `pulsegrid_backfill_pipeline`: silver full refresh -> gold rebuild

## Local Run

From `backend/`:

```bash
dagster dev -f orchestration/dagster_defs.py
```

Then launch jobs from the Dagster UI.

## Notes

- This is intentionally startup-practical: it wraps existing job entrypoints.
- Backfill uses `SILVER_FULL_REFRESH=true` to rebuild Silver from Bronze.
