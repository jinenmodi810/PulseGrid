"""Zone ids aligned with Flutter ``kAuthZoneIds`` (chip labels are UI-only).

Flutter sends canonical ids: ``zone-riverside``, ``zone-central``, ``zone-north``, ``zone-east``.
The API also accepts bare slug names (``riverside``, ``Riverside``) for Swagger convenience.
"""

from __future__ import annotations

# Must match ``lib/features/auth/presentation/constants/zone_options.dart`` kAuthZoneIds.
CANONICAL_ZONE_IDS: tuple[str, ...] = (
    "zone-riverside",
    "zone-central",
    "zone-north",
    "zone-east",
)

ZONE_LABELS: dict[str, str] = {
    "zone-riverside": "Riverside",
    "zone-central": "Central",
    "zone-north": "North",
    "zone-east": "East",
}

# Lowercased keys → canonical id (includes chip label → id).
_ZONE_ALIASES: dict[str, str] = {
    "zone-riverside": "zone-riverside",
    "zone-central": "zone-central",
    "zone-north": "zone-north",
    "zone-east": "zone-east",
    "riverside": "zone-riverside",
    "central": "zone-central",
    "north": "zone-north",
    "east": "zone-east",
}


def normalize_zone_id(raw: str) -> str | None:
    """Return canonical zone id for DB/FK, or None if unknown."""
    s = (raw or "").strip().lower().replace("_", "-")
    if not s:
        return None
    return _ZONE_ALIASES.get(s)


def normalize_zone_ids(raw: list[str]) -> list[str]:
    """Deduplicated canonical zone ids (order preserved)."""
    out: list[str] = []
    for item in raw:
        c = normalize_zone_id(str(item))
        if c is not None and c not in out:
            out.append(c)
    return out


def zone_display_name(zone_id: str) -> str:
    return ZONE_LABELS.get(zone_id.strip(), zone_id.strip())
