import subprocess
from datetime import datetime

from dagster import Definitions, In, Nothing, job, op


def _run_cmd(context, cmd: list[str]) -> None:
    context.log.info("running: %s", " ".join(cmd))
    subprocess.run(cmd, check=True)


@op
def outbox_publish_once(context) -> None:
    _run_cmd(context, ["python", "-m", "app.jobs.outbox_publisher"])


@op(ins={"start_after": In(Nothing)})
def bronze_once(context) -> None:
    _run_cmd(context, ["python", "-m", "app.jobs.bronze_ingestor"])


@op(ins={"start_after": In(Nothing)})
def silver_once(context) -> None:
    _run_cmd(context, ["python", "-m", "app.jobs.silver_etl"])


@op(ins={"start_after": In(Nothing)})
def gold_once(context) -> None:
    _run_cmd(context, ["python", "-m", "app.jobs.gold_etl"])


@job
def pulsegrid_hourly_pipeline() -> None:
    outbox_done = outbox_publish_once()
    bronze_done = bronze_once(outbox_done)
    silver_done = silver_once(bronze_done)
    gold_once(silver_done)


@op(ins={"start_after": In(Nothing)})
def full_refresh_silver(context) -> None:
    _run_cmd(context, ["bash", "-lc", "SILVER_FULL_REFRESH=true python -m app.jobs.silver_etl"])


@job
def pulsegrid_backfill_pipeline() -> None:
    silver_done = full_refresh_silver(outbox_publish_once())
    gold_once(silver_done)


defs = Definitions(jobs=[pulsegrid_hourly_pipeline, pulsegrid_backfill_pipeline])
