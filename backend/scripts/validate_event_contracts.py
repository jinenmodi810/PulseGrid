"""Quick local validator for outbox event contracts."""

from __future__ import annotations

import json

from app.domain.event_streaming import validate_event_envelope


def main() -> None:
    valid = {
        "event_id": "38cd59cf-e075-4544-922e-9fb93a71cc71",
        "event_type": "incident.created",
        "event_version": 1,
        "schema_version": 1,
        "aggregate_type": "incident",
        "aggregate_id": "c3349ab7-1a23-43b1-a372-655cc17df3ad",
        "enqueued_at": "2026-04-25T03:06:16.207Z",
        "payload": {
            "incident_id": "c3349ab7-1a23-43b1-a372-655cc17df3ad",
            "zone_id": "zone-central",
            "status": "open",
            "priority_label": "CRITICAL",
            "reporter_user_id": "victim-user-123",
            "occurred_at": "2026-04-25T03:06:16Z",
            "rejection_count": 0,
        },
    }
    invalid = {
        **valid,
        "payload": {
            "zone_id": "zone-central",
            "status": "open",
            "priority_label": "CRITICAL",
            "reporter_user_id": "victim-user-123",
            "occurred_at": "2026-04-25T03:06:16Z",
            "rejection_count": 0,
        },
    }

    validate_event_envelope(valid)
    print("valid event: PASS")
    try:
        validate_event_envelope(invalid)
        print("invalid event: UNEXPECTED PASS")
    except Exception as exc:  # noqa: BLE001
        print(f"invalid event: PASS ({exc})")

    print(json.dumps(valid, indent=2))


if __name__ == "__main__":
    main()
