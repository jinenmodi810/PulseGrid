"""Incident priority scoring — demo weights aligned with Flutter preview endpoint."""

from __future__ import annotations

from app.models.incident_requests import PriorityPreviewRequest


def compute_priority_score_and_label(
    *,
    severity: str = "medium",
    people_count: int = 1,
    elderly: bool = False,
    child_present: bool = False,
    injury: bool = False,
    oxygen_required: bool = False,
    shelter_needed: bool = False,
    food_needed: bool = False,
    transport_needed: bool = False,
) -> tuple[float, str]:
    """Return numeric score (0–100) and label LOW | MEDIUM | HIGH | CRITICAL."""
    sev = (severity or "medium").lower()
    base = {"low": 12.0, "medium": 28.0, "high": 48.0, "critical": 68.0}.get(sev, 28.0)
    score = base
    if elderly:
        score += 10.0
    if child_present:
        score += 8.0
    if injury:
        score += 12.0
    if oxygen_required:
        score += 14.0
    if shelter_needed:
        score += 6.0
    if food_needed:
        score += 4.0
    if transport_needed:
        score += 5.0
    if people_count > 1:
        score += min(12.0, float(people_count - 1) * 3.0)
    score = min(100.0, round(score, 2))

    if score >= 82.0:
        label = "CRITICAL"
    elif score >= 58.0:
        label = "HIGH"
    elif score >= 32.0:
        label = "MEDIUM"
    else:
        label = "LOW"
    return score, label


def preview_from_request(body: PriorityPreviewRequest) -> tuple[float, str]:
    return compute_priority_score_and_label(
        severity=body.severity,
        people_count=body.people_count,
        elderly=body.elderly,
        child_present=body.child_present,
        injury=body.injury,
        oxygen_required=body.oxygen_required,
        shelter_needed=body.shelter_needed,
        food_needed=body.food_needed,
        transport_needed=body.transport_needed,
    )
