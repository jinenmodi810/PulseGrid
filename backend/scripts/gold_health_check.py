"""Gold marts health check."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import boto3
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


def _list_keys(client: Any, bucket: str, prefix: str) -> list[str]:
    out: list[str] = []
    token = None
    while True:
        kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
        if token:
            kwargs["ContinuationToken"] = token
        resp = client.list_objects_v2(**kwargs)
        for obj in resp.get("Contents") or []:
            key = str(obj.get("Key") or "")
            if key:
                out.append(key)
        if not resp.get("IsTruncated"):
            break
        token = resp.get("NextContinuationToken")
        if not token:
            break
    return out


def _latest_key(keys: list[str]) -> str | None:
    if not keys:
        return None
    return sorted(keys)[-1]


def main() -> None:
    s = get_settings()
    client = _s3_client()
    print("=== PulseGrid Gold Health Check ===")
    print(f"bucket={s.GOLD_BUCKET}")
    print(f"gold_prefix={s.GOLD_PREFIX}")
    print(f"gold_rejected_prefix={s.GOLD_REJECTED_PREFIX}")
    try:
        client.head_bucket(Bucket=s.GOLD_BUCKET)
        print("bucket_available=true")
    except Exception as exc:  # noqa: BLE001
        print("bucket_available=false")
        print(f"error={str(exc)}")
        return

    fact_incident = _list_keys(client, s.GOLD_BUCKET, f"{s.GOLD_PREFIX}/fact_incident_lifecycle/")
    fact_volunteer = _list_keys(client, s.GOLD_BUCKET, f"{s.GOLD_PREFIX}/fact_volunteer_performance/")
    fact_org = _list_keys(client, s.GOLD_BUCKET, f"{s.GOLD_PREFIX}/fact_org_capacity/")
    dim_time = _list_keys(client, s.GOLD_BUCKET, f"{s.GOLD_PREFIX}/dim_time/")
    rejected = _list_keys(client, s.GOLD_BUCKET, f"{s.GOLD_REJECTED_PREFIX}/")

    print(f"fact_incident_files={len([k for k in fact_incident if k.endswith('.parquet')])}")
    print(f"fact_volunteer_files={len([k for k in fact_volunteer if k.endswith('.parquet')])}")
    print(f"fact_org_files={len([k for k in fact_org if k.endswith('.parquet')])}")
    print(f"dim_time_files={len([k for k in dim_time if k.endswith('.parquet')])}")
    print(f"gold_rejected_files={len(rejected)}")
    print(f"latest_gold_artifact={_latest_key(fact_incident + fact_volunteer + fact_org + dim_time) or 'none'}")


if __name__ == "__main__":
    main()
