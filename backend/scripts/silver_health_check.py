"""Silver ETL health check for MinIO/S3 output."""

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


def _latest_partition(keys: list[str], base: str) -> str | None:
    parts = [k[len(base) :].strip("/") for k in keys if k.startswith(base)]
    if not parts:
        return None
    return sorted(parts)[-1]


def main() -> None:
    s = get_settings()
    client = _s3_client()
    print("=== PulseGrid Silver Health Check ===")
    print(f"bucket={s.SILVER_BUCKET}")
    print(f"silver_prefix={s.SILVER_PREFIX}")
    print(f"rejected_prefix={s.SILVER_REJECTED_PREFIX}")
    try:
        client.head_bucket(Bucket=s.SILVER_BUCKET)
        print("bucket_available=true")
    except Exception as exc:  # noqa: BLE001
        print("bucket_available=false")
        print(f"error={str(exc)}")
        return

    base = f"{s.SILVER_PREFIX}/"
    incident_keys = _list_keys(client, s.SILVER_BUCKET, f"{base}incident_events/")
    organization_keys = _list_keys(client, s.SILVER_BUCKET, f"{base}organization_events/")
    volunteer_keys = _list_keys(client, s.SILVER_BUCKET, f"{base}volunteer_events/")
    rejected_keys = _list_keys(client, s.SILVER_BUCKET, f"{s.SILVER_REJECTED_PREFIX}/")

    print(f"silver_incident_files={len([k for k in incident_keys if k.endswith('.parquet')])}")
    print(f"silver_organization_files={len([k for k in organization_keys if k.endswith('.parquet')])}")
    print(f"silver_volunteer_files={len([k for k in volunteer_keys if k.endswith('.parquet')])}")
    print(f"silver_rejected_files={len(rejected_keys)}")

    latest_incident = _latest_partition(incident_keys, f"{base}incident_events/")
    latest_org = _latest_partition(organization_keys, f"{base}organization_events/")
    latest_vol = _latest_partition(volunteer_keys, f"{base}volunteer_events/")
    print(f"latest_incident_partition={latest_incident or 'none'}")
    print(f"latest_organization_partition={latest_org or 'none'}")
    print(f"latest_volunteer_partition={latest_vol or 'none'}")


if __name__ == "__main__":
    main()
