"""Kafka/Redpanda -> Bronze (MinIO/S3) raw event ingestion."""

from __future__ import annotations

import json
import logging
import time
import gzip
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from app.core.config import get_settings
from app.observability.lineage import emit_lineage_event
from app.observability.metrics import (
    bronze_ingestor_dead_letter_total,
    bronze_ingestor_written_total,
    update_runtime_metric,
)

_log = logging.getLogger("pulsegrid.bronze_ingestor")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _parse_iso(ts: str | None) -> datetime:
    if not ts:
        return datetime.now(tz=timezone.utc)
    s = str(ts).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return datetime.now(tz=timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _domain_from_event_type(event_type: str) -> str:
    et = str(event_type or "").strip()
    if et.startswith("incident."):
        return "incident"
    if et.startswith("organization."):
        return "organization"
    if et.startswith("volunteer."):
        return "volunteer"
    return "audit"


def _object_key(envelope: dict[str, Any]) -> str:
    event_type = str(envelope.get("event_type") or "unknown")
    domain = _domain_from_event_type(event_type)
    event_id = str(envelope.get("event_id") or "").strip()
    if not event_id:
        event_id = f"missing-id-{int(time.time() * 1000)}"
    ts = _parse_iso(str(envelope.get("enqueued_at") or ""))
    return (
        f"{get_settings().BRONZE_PREFIX}/{domain}/"
        f"event_type={event_type}/year={ts:%Y}/month={ts:%m}/day={ts:%d}/hour={ts:%H}/"
        f"{event_id}{_extension()}"
    )


def _dead_letter_key(now: datetime | None = None) -> str:
    ts = (now or datetime.now(tz=timezone.utc)).astimezone(timezone.utc)
    return (
        f"{get_settings().BRONZE_PREFIX}/_dead_letter/"
        f"year={ts:%Y}/month={ts:%m}/day={ts:%d}/hour={ts:%H}/"
        f"{uuid.uuid4()}{_extension()}"
    )


def _extension() -> str:
    return ".json.gz" if bool(get_settings().BRONZE_GZIP_ENABLED) else ".json"


def _s3_client():
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.BRONZE_S3_ENDPOINT_URL,
        aws_access_key_id=s.BRONZE_S3_ACCESS_KEY,
        aws_secret_access_key=s.BRONZE_S3_SECRET_KEY,
        region_name=s.BRONZE_S3_REGION,
        use_ssl=bool(s.BRONZE_S3_USE_SSL),
    )


def _ensure_bucket_exists(client: Any, bucket: str) -> None:
    try:
        client.head_bucket(Bucket=bucket)
        return
    except ClientError:
        pass
    client.create_bucket(Bucket=bucket)
    _log.info("bronze_bucket_created bucket=%s", bucket)


def _already_written(client: Any, bucket: str, key: str) -> bool:
    try:
        client.head_object(Bucket=bucket, Key=key)
        return True
    except ClientError:
        return False


def _write_raw_event(client: Any, bucket: str, envelope: dict[str, Any]) -> tuple[bool, str]:
    key = _object_key(envelope)
    # Idempotency: event_id-based deterministic key; skip if object already exists.
    if _already_written(client, bucket, key):
        return False, key
    body = _serialize_payload(envelope)
    client.put_object(Bucket=bucket, Key=key, Body=body, ContentType="application/json")
    return True, key


def _serialize_payload(data: dict[str, Any]) -> bytes:
    raw = (json.dumps(data, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")
    if bool(get_settings().BRONZE_GZIP_ENABLED):
        return gzip.compress(raw)
    return raw


def _safe_raw_value(raw_value: Any) -> Any:
    if isinstance(raw_value, (dict, list, str, int, float, bool)) or raw_value is None:
        return raw_value
    if isinstance(raw_value, (bytes, bytearray)):
        return bytes(raw_value).decode("utf-8", errors="replace")[:2000]
    return str(raw_value)[:2000]


def _write_dead_letter(
    client: Any,
    bucket: str,
    *,
    error_type: str,
    error_message: str,
    raw_value: Any,
    topic: str,
    partition: int,
    offset: int,
) -> str:
    payload = {
        "error_type": error_type,
        "error_message": error_message[:1000],
        "raw_value": _safe_raw_value(raw_value),
        "topic": topic,
        "partition": partition,
        "offset": offset,
        "captured_at": datetime.now(tz=timezone.utc).isoformat(),
    }
    key = _dead_letter_key()
    client.put_object(Bucket=bucket, Key=key, Body=_serialize_payload(payload), ContentType="application/json")
    return key


def _route_invalid_envelope_to_dead_letter(
    client: Any,
    bucket: str,
    *,
    envelope: Any,
    error_code: str,
    topic: str,
    partition: int,
    offset: int,
) -> str:
    return _write_dead_letter(
        client,
        bucket,
        error_type=error_code,
        error_message=f"invalid/unexpected envelope shape: {error_code}",
        raw_value=envelope,
        topic=topic,
        partition=partition,
        offset=offset,
    )


def _validate_envelope_shape(envelope: dict[str, Any]) -> tuple[bool, str]:
    if not isinstance(envelope, dict):
        return False, "envelope_not_object"
    event_id = str(envelope.get("event_id") or "").strip()
    if not event_id:
        return False, "missing_event_id"
    event_type = str(envelope.get("event_type") or "").strip()
    if not event_type:
        return False, "missing_event_type"
    if "payload" not in envelope:
        return False, "missing_payload"
    return True, ""


def _topics_from_settings() -> list[str]:
    raw = str(get_settings().BRONZE_KAFKA_TOPICS or "").strip()
    return [x.strip() for x in raw.split(",") if x.strip()]


def run_once(max_records: int = 500) -> dict[str, int]:
    """Process at most one poll batch for demo/automation usage."""
    settings = get_settings()
    brokers = (settings.KAFKA_BOOTSTRAP_SERVERS or "").strip()
    if not brokers:
        raise RuntimeError("KAFKA_BOOTSTRAP_SERVERS is required for bronze ingestion.")
    topics = _topics_from_settings()
    if not topics:
        raise RuntimeError("BRONZE_KAFKA_TOPICS is empty.")

    from kafka import KafkaConsumer

    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=[b.strip() for b in brokers.split(",") if b.strip()],
        group_id=settings.BRONZE_KAFKA_CONSUMER_GROUP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    try:
        s3 = _s3_client()
        _ensure_bucket_exists(s3, settings.BRONZE_BUCKET)
        consumed = 0
        written = 0
        skipped_duplicate = 0
        failed = 0
        dead_letter_written = 0
        batches = consumer.poll(timeout_ms=int(settings.BRONZE_POLL_TIMEOUT_MS), max_records=max_records)
        for _tp, messages in batches.items():
            for msg in messages:
                consumed += 1
                try:
                    raw = msg.value
                    try:
                        decoded = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
                        envelope = json.loads(decoded)
                    except Exception as exc:  # noqa: BLE001
                        failed += 1
                        dl_key = _write_dead_letter(
                            s3,
                            settings.BRONZE_BUCKET,
                            error_type="malformed_json",
                            error_message=str(exc),
                            raw_value=raw,
                            topic=msg.topic,
                            partition=msg.partition,
                            offset=msg.offset,
                        )
                        dead_letter_written += 1
                        bronze_ingestor_dead_letter_total.inc()
                        update_runtime_metric("bronze_dead_letter", dead_letter_written)
                        _log.error("bronze_dead_letter_written key=%s topic=%s partition=%s offset=%s", dl_key, msg.topic, msg.partition, msg.offset)
                        continue
                    ok, error_code = _validate_envelope_shape(envelope if isinstance(envelope, dict) else {})
                    if not ok:
                        failed += 1
                        dl_key = _route_invalid_envelope_to_dead_letter(
                            s3,
                            settings.BRONZE_BUCKET,
                            envelope=envelope,
                            error_code=error_code,
                            topic=msg.topic,
                            partition=msg.partition,
                            offset=msg.offset,
                        )
                        dead_letter_written += 1
                        bronze_ingestor_dead_letter_total.inc()
                        update_runtime_metric("bronze_dead_letter", dead_letter_written)
                        _log.error("bronze_dead_letter_written key=%s topic=%s partition=%s offset=%s", dl_key, msg.topic, msg.partition, msg.offset)
                        continue
                    did_write, key = _write_raw_event(s3, settings.BRONZE_BUCKET, envelope)
                    if did_write:
                        written += 1
                        bronze_ingestor_written_total.inc()
                        update_runtime_metric("bronze_written", written)
                        _log.info("bronze_event_written topic=%s partition=%s offset=%s key=%s", msg.topic, msg.partition, msg.offset, key)
                    else:
                        skipped_duplicate += 1
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    try:
                        dl_key = _write_dead_letter(
                            s3,
                            settings.BRONZE_BUCKET,
                            error_type="write_failure",
                            error_message=str(exc),
                            raw_value=msg.value,
                            topic=msg.topic,
                            partition=msg.partition,
                            offset=msg.offset,
                        )
                        dead_letter_written += 1
                        bronze_ingestor_dead_letter_total.inc()
                        update_runtime_metric("bronze_dead_letter", dead_letter_written)
                        _log.error("bronze_dead_letter_written key=%s topic=%s partition=%s offset=%s", dl_key, msg.topic, msg.partition, msg.offset)
                    except Exception:  # noqa: BLE001
                        _log.exception("bronze_dead_letter_write_failed")
        summary = {
            "consumed": consumed,
            "written": written,
            "skipped_duplicate": skipped_duplicate,
            "failed": failed,
            "dead_letter_written": dead_letter_written,
        }
        emit_lineage_event(
            job_name="bronze_ingestor",
            status="success",
            inputs=[f"kafka://{topic}" for topic in topics],
            outputs=[f"s3://{settings.BRONZE_BUCKET}/{settings.BRONZE_PREFIX}/"],
            run_stats=summary,
        )
        return summary
    finally:
        consumer.close()


def main_loop() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
    settings = get_settings()
    brokers = (settings.KAFKA_BOOTSTRAP_SERVERS or "").strip()
    if not brokers:
        raise RuntimeError("KAFKA_BOOTSTRAP_SERVERS is required for bronze ingestion.")
    topics = _topics_from_settings()
    if not topics:
        raise RuntimeError("BRONZE_KAFKA_TOPICS is empty.")

    consumed = 0
    written = 0
    skipped_duplicate = 0
    failed = 0
    dead_letter_written = 0
    _log.info("bronze_ingestor_start topics=%s bucket=%s", ",".join(topics), settings.BRONZE_BUCKET)
    while True:
        batch = run_once(max_records=500)
        consumed += int(batch["consumed"])
        written += int(batch["written"])
        skipped_duplicate += int(batch["skipped_duplicate"])
        failed += int(batch["failed"])
        dead_letter_written += int(batch["dead_letter_written"])
        _log.info(
            "bronze_ingestor_stats consumed=%s written=%s skipped_duplicate=%s failed=%s dead_letter_written=%s",
            consumed,
            written,
            skipped_duplicate,
            failed,
            dead_letter_written,
        )


if __name__ == "__main__":
    main_loop()
