"""Central deterministic response-tier engine (mother brain). AI must not call this layer."""

from __future__ import annotations

import re

from app.models.response_tier_models import (
    ResponseTierInput,
    ResponseTierName,
    ResponseTierPlan,
    ResponseTierReason,
)


def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _disaster_bucket(incident_type: str) -> set[str]:
    """Coarse tags from free-text incident_type."""
    t = _norm(incident_type)
    tags: set[str] = set()
    if re.search(r"\bfood\b|food_support|hunger|meal", t):
        tags.add("food")
    if re.search(r"\bflood\b|flooding|inundation", t):
        tags.add("flood")
    if re.search(r"\bfire\b|wildfire|burn", t):
        tags.add("fire")
    if re.search(r"\bearthquake\b|seismic|collapse|structural", t):
        tags.add("earthquake")
    if re.search(r"\bmedical\b|clinic|hospital|ambulance|trauma|injury", t):
        tags.add("medical")
    if re.search(r"\bshelter\b|housing|evacuat", t):
        tags.add("shelter_keyword")
    if re.search(r"\btransport\b|ride|evacuation vehicle", t):
        tags.add("transport_keyword")
    return tags


def _severity_rank(severity: str) -> int:
    m = {"low": 1, "medium": 2, "moderate": 2, "high": 3, "critical": 4, "severe": 4}
    return m.get(_norm(severity), 2)


def _priority_rank(label: str) -> int:
    u = (label or "").upper()
    if "CRITICAL" in u or "URGENT" in u:
        return 4
    if "HIGH" in u:
        return 3
    if "MEDIUM" in u or "MODERATE" in u:
        return 2
    return 1


def determine_response_tier(inp: ResponseTierInput) -> ResponseTierPlan:
    """
    Decide collaboration shape from incident + profile context only.
    Matching availability is handled later in incident_service.
    """
    reasons: list[ResponseTierReason] = []
    it = _norm(inp.incident_type)
    tags = _disaster_bucket(inp.incident_type)
    sev_r = _severity_rank(inp.severity)
    pr_r = _priority_rank(inp.priority_label)
    people = max(1, int(inp.people_count or 1))
    hz = int(inp.household_size or people)

    medical_institutional = bool(
        inp.injury
        or inp.oxygen_required
        or inp.oxygen_dependency_profile
        or "medical" in tags
        or "medical" in it
    )
    if medical_institutional:
        reasons.append(
            ResponseTierReason(
                code="medical_institutional",
                detail="Medical or oxygen need requires institutional capacity.",
            )
        )

    disaster_org = bool(
        "fire" in tags
        or "earthquake" in tags
        or ("flood" in tags and (inp.shelter_needed or inp.transport_needed or people >= 4))
        or (inp.shelter_needed and people >= 4)
        or (inp.shelter_needed and hz >= 4)
    )
    if disaster_org and not medical_institutional:
        reasons.append(
            ResponseTierReason(
                code="disaster_institutional",
                detail="Disaster profile indicates organized response (shelter/capacity or hazard type).",
            )
        )

    institutional_need = medical_institutional or disaster_org

    local_volunteer_valuable = bool(
        inp.food_needed
        or (inp.transport_needed and not inp.injury)
        or inp.elderly
        or inp.child_present
        or inp.mobility_concern
        or (inp.shelter_needed and people < 4 and not ("fire" in tags or "earthquake" in tags))
    )

    food_onlyish = ("food" in tags or inp.food_needed) and not institutional_need and sev_r <= 2 and pr_r <= 2

    # --- Decide intended tier ---
    if food_onlyish and not inp.injury and not inp.oxygen_required:
        reasons.append(
            ResponseTierReason(
                code="community_support",
                detail="Low-acuity community support; local volunteers are appropriate.",
            )
        )
        return ResponseTierPlan(
            intended_tier=ResponseTierName.volunteer_only,
            seek_volunteer=True,
            seek_organization=False,
            reasons=reasons,
            decision_summary="Local volunteer support is sufficient for this request profile.",
            high_acuity=False,
        )

    if institutional_need and local_volunteer_valuable and not (inp.injury and inp.oxygen_required):
        reasons.append(
            ResponseTierReason(
                code="dual_response",
                detail="Immediate neighbor support plus institutional capacity both add value.",
            )
        )
        return ResponseTierPlan(
            intended_tier=ResponseTierName.volunteer_plus_organization,
            seek_volunteer=True,
            seek_organization=True,
            reasons=reasons,
            decision_summary="Deploy local volunteers while activating partner organization capacity.",
            high_acuity=sev_r >= 3 or pr_r >= 3,
        )

    if institutional_need:
        reasons.append(
            ResponseTierReason(
                code="organization_led",
                detail="Institutional partners should lead this response.",
            )
        )
        return ResponseTierPlan(
            intended_tier=ResponseTierName.organization_only,
            seek_volunteer=False,
            seek_organization=True,
            reasons=reasons,
            decision_summary="Partner organizations should handle this incident.",
            high_acuity=sev_r >= 3 or pr_r >= 3 or inp.injury or inp.oxygen_required,
        )

    # Default: manageable local incident
    reasons.append(
        ResponseTierReason(
            code="local_volunteer_default",
            detail="Severity and needs are within typical volunteer scope.",
        )
    )
    return ResponseTierPlan(
        intended_tier=ResponseTierName.volunteer_only,
        seek_volunteer=True,
        seek_organization=False,
        reasons=reasons,
        decision_summary="Volunteer-led response is appropriate.",
        high_acuity=False,
    )


def merge_plan_reasons(plan: ResponseTierPlan, extra: list[ResponseTierReason]) -> list[ResponseTierReason]:
    return [*plan.reasons, *extra]


def augment_tier_reasons_for_matching(
    plan: ResponseTierPlan,
    *,
    volunteer_selected: bool,
    organization_selected: bool,
    rejected_volunteers: list[dict[str, str]],
    rejected_organizations: list[dict[str, str]],
) -> list[ResponseTierReason]:
    """Append explainable post-match notes (deterministic; not ML)."""
    extra: list[ResponseTierReason] = []
    if plan.seek_volunteer and not volunteer_selected:
        vol_bits = [
            f"{r.get('name', '')}:{r.get('reason', '')}"
            for r in (rejected_volunteers or [])[:3]
            if isinstance(r, dict)
        ]
        top = "; ".join(vol_bits)
        detail = "No volunteer was selected in this pass."
        if top:
            detail += f" Sample rejections: {top}."
        extra.append(ResponseTierReason(code="volunteer_matching_gap", detail=detail))
    if plan.seek_organization and not organization_selected:
        org_bits = [
            f"{r.get('name', '')}:{r.get('reason', '')}"
            for r in (rejected_organizations or [])[:3]
            if isinstance(r, dict)
        ]
        top_o = "; ".join(org_bits)
        detail_o = "No organization was selected in this pass."
        if top_o:
            detail_o += f" Sample rejections: {top_o}."
        extra.append(ResponseTierReason(code="organization_matching_gap", detail=detail_o))
    return extra


def _is_critical(severity: str, priority_label: str) -> bool:
    if _norm(severity) in ("critical", "severe"):
        return True
    u = (priority_label or "").upper()
    return "CRITICAL" in u or "URGENT" in u


def finalize_response_after_matching(
    plan: ResponseTierPlan,
    *,
    volunteer_selected: bool,
    organization_selected: bool,
    severity: str,
    priority_label: str,
) -> tuple[str, bool, str]:
    """
    Combine the pre-match plan with assignment outcomes.

    Returns (response_tier, escalation_required, decision_summary).

    escalation_required is an operations / safety flag (urgent attention), not always identical to tier name.
    """
    it = plan.intended_tier
    crit = _is_critical(severity, priority_label)

    if it == ResponseTierName.volunteer_only:
        if volunteer_selected:
            return (
                ResponseTierName.volunteer_only.value,
                crit,
                plan.decision_summary + " A volunteer is assigned.",
            )
        if crit or plan.high_acuity:
            return (
                ResponseTierName.escalation_required.value,
                True,
                "No volunteer was available while indicators required a timely local response. Escalation is required.",
            )
        return (
            ResponseTierName.volunteer_only.value,
            False,
            plan.decision_summary + " No volunteer is assigned yet; automated matching continues.",
        )

    if it == ResponseTierName.organization_only:
        if not organization_selected:
            return (
                ResponseTierName.escalation_required.value,
                True,
                "Institutional response was required but no partner organization had suitable verified capacity.",
            )
        return (
            ResponseTierName.organization_only.value,
            crit,
            plan.decision_summary + " A partner organization is assigned to lead the response.",
        )

    # volunteer_plus_organization
    if volunteer_selected and organization_selected:
        return (
            ResponseTierName.volunteer_plus_organization.value,
            crit,
            plan.decision_summary + " A volunteer and an organization are both attached for coordinated response.",
        )
    if organization_selected and not volunteer_selected:
        return (
            ResponseTierName.organization_only.value,
            crit,
            "Organization-led response is active; volunteer assignment is still pending where it remains safe to add.",
        )
    if volunteer_selected and not organization_selected:
        return (
            ResponseTierName.escalation_required.value,
            True,
            "Volunteers are helping locally, but required institutional capacity could not be matched in this pass.",
        )
    return (
        ResponseTierName.escalation_required.value,
        True,
        "Both volunteer and institutional channels were needed; neither had confirmed capacity in the initial window.",
    )
