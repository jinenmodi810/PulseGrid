"""Bronze lake quick health check (MinIO/S3-compatible)."""

from __future__ import annotations

from typing import Any
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from app.core.config import get_settings

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def _s3_client() -> Any:
    s = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=s.BRONZE_S3_ENDPOINT_URL,
        aws_access_key_id=s.BRONZE_S3_ACCESS_KEY,
        aws_secret_access_key=s.BRONZE_S3_SECRET_KEY,
        region_name=s.BRONZE_S3_REGION,
        use_ssl=bool(s.BRONZE_S3_USE_SSL),
    )


def _count_prefix(client: Any, bucket: str, prefix: str, max_keys: int = 1000) -> int:
    count = 0
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": max_keys}
        if token:
            kwargs["ContinuationToken"] = token
        resp = client.list_objects_v2(**kwargs)
        count += int(resp.get("KeyCount") or 0)
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return count


def main() -> None:
    s = get_settings()
    client = _s3_client()
    print("=== PulseGrid Bronze Health Check ===")
    print(f"bucket={s.BRONZE_BUCKET}")
    print(f"prefix={s.BRONZE_PREFIX}")
    print(f"topics={s.BRONZE_KAFKA_TOPICS}")
    print(f"gzip_enabled={bool(s.BRONZE_GZIP_ENABLED)}")
    try:
        client.head_bucket(Bucket=s.BRONZE_BUCKET)
        print("bucket_available=true")
    except Exception as exc:  # noqa: BLE001
        print("bucket_available=false")
        print(f"error={str(exc)}")
        return

    raw_prefix = f"{s.BRONZE_PREFIX}/"
    dlq_prefix = f"{s.BRONZE_PREFIX}/_dead_letter/"
    raw_count = _count_prefix(client, s.BRONZE_BUCKET, raw_prefix)
    dlq_count = _count_prefix(client, s.BRONZE_BUCKET, dlq_prefix)
    # raw_count includes dead-letter; subtract for quick practical split.
    raw_data_count = max(0, raw_count - dlq_count)
    print(f"raw_objects_count={raw_data_count}")
    print(f"dead_letter_objects_count={dlq_count}")


if __name__ == "__main__":
    main()
