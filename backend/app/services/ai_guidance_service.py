"""Role-specific AI guidance built from trusted Neo4j state — Gemini explains; backend decides."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.core.config import get_settings
from app.core.neo4j_client import get_driver, managed_neo4j_session
from app.db.queries import incident_queries
from app.models.ai_guidance_models import (
    AffectedUserGuidanceRequest,
    CoordinatorSummaryRequest,
    GuidanceResponse,
    IncidentGuidanceBundleResponse,
    VolunteerGuidanceRequest,
)
from app.services.gemini_service import (
    GeminiGenerationError,
    GeminiUnavailableError,
    get_gemini_text_client,
)


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _props(node: Any) -> dict[str, Any]:
    if node is None:
        return {}
    if hasattr(node, "items"):
        return dict(node)
    return {}


def _load_ai_context(*, incident_id: str) -> dict[str, Any] | None:
    driver = get_driver()
    settings = get_settings()

    def read(tx: Any) -> dict[str, Any] | None:
        rec = tx.run(incident_queries.GET_INCIDENT_AI_CONTEXT, incident_id=incident_id).single()
        if rec is None or rec.get("incident") is None:
            return None
        inc = _props(rec["incident"])
        rep = _props(rec.get("reporter"))
        vol = _props(rec.get("volunteer"))
        return {"incident": inc, "reporter": rep, "volunteer": vol}

    with managed_neo4j_session(driver, settings) as session:
        return session.execute_read(read)


def _language_from_context(ctx: dict[str, Any]) -> str:
    inc = ctx.get("incident") or {}
    rep = ctx.get("reporter") or {}
    lang = str(inc.get("preferred_language") or rep.get("preferred_language") or "en").strip() or "en"
    return lang[:12]


def _language_instruction(lang: str) -> str:
    if lang.lower() in ("en", "english", ""):
        return "Write in clear, simple English."
    if lang.lower() in ("es", "spanish"):
        return "Write in clear Spanish (neutral Latin American)."
    return f"Write in the language best matching BCP-47 tag '{lang}'. If unsure, use English."


# --- Deterministic fallbacks (mandatory when Gemini fails) ---

def _fallback_affected(ctx: dict[str, Any]) -> str:
    status = str((ctx.get("incident") or {}).get("status") or "open")
    if status.lower() in ("resolved",):
        return (
            "Your request has been marked resolved. If you still need help, submit a new update or contact support. "
            "Keep your phone nearby for any follow-up."
        )
    return (
        "Your request has been received and is being processed. Please remain in the safest accessible location, "
        "keep your phone nearby, and watch this screen for updates."
    )


def _fallback_volunteer() -> str:
    return (
        "You have been assigned to a support request. Review the needs carefully, confirm conditions are safe, "
        "and proceed only when you are ready. Bring any usual safety items your organization recommends."
    )


def _fallback_coordinator() -> str:
    return (
        "High-priority incident under review. Check assignment status, risk flags (elderly, oxygen, transport), "
        "and current support availability before releasing updates to the field."
    )


def _build_affected_prompt(ctx: dict[str, Any]) -> str:
    inc = ctx["incident"]
    rep = ctx.get("reporter") or {}
    vol = ctx.get("volunteer") or {}
    lang = _language_from_context(ctx)
    assigned = bool(vol.get("id"))
    assign_name = str(vol.get("display_name") or "").strip()
    flags = []
    for key, label in (
        ("elderly", "elderly present"),
        ("child_present", "child present"),
        ("injury", "injury"),
        ("oxygen_required", "oxygen support"),
        ("shelter_needed", "shelter"),
        ("food_needed", "food"),
        ("transport_needed", "transport"),
    ):
        if inc.get(key):
            flags.append(label)
    flag_line = ", ".join(flags) if flags else "no special flags recorded"

    return f"""You are PulseGrid, a crisis coordination assistant. Output ONLY the guidance paragraph for the affected person — no title, no bullet list, no JSON.

CRITICAL RULES:
- Do NOT change or restate priority scores, routing decisions, or volunteer assignment outcomes; those are already decided by the system.
- Be calm, reassuring, and practical. No panic language. No guarantees about arrival times unless the data below explicitly includes an ETA.
- Mention an assigned helper only if assigned_helper_present is true; use the helper display name if provided.
- {_language_instruction(lang)}

Structured facts (trusted):
- incident_type: {inc.get("incident_type", "")}
- status: {inc.get("status", "")}
- severity: {inc.get("severity", "")}
- priority_label: {inc.get("priority_label", "")}
- zone_id: {inc.get("zone_id", "")}
- people_count: {inc.get("people_count", "")}
- needs_flags: {flag_line}
- route_status: {inc.get("route_status", "")}
- assigned_helper_present: {assigned}
- assigned_helper_name: {assign_name or "n/a"}
- preferred_language_tag: {lang}
- emergency_contact_on_file: {bool(rep.get("emergency_contact_name") or inc.get("emergency_contact_name"))}

Write 3–5 short sentences suitable for a mobile screen.
"""


def _build_volunteer_prompt(ctx: dict[str, Any], volunteer_id: str) -> str:
    inc = ctx["incident"]
    rep = ctx.get("reporter") or {}
    vol = ctx.get("volunteer") or {}
    lang = _language_from_context(ctx)
    flags = []
    for key, label in (
        ("elderly", "elderly"),
        ("child_present", "child"),
        ("injury", "injury"),
        ("oxygen_required", "oxygen"),
        ("shelter_needed", "shelter"),
        ("food_needed", "food"),
        ("transport_needed", "transport"),
    ):
        if inc.get(key):
            flags.append(label)
    if rep.get("mobility_concern"):
        flags.append("mobility (household)")
    flag_line = ", ".join(flags) if flags else "none highlighted"

    vskills = vol.get("skills") or vol.get("skill_type") or ""
    vsupport = vol.get("support_types") or ""
    return f"""You are PulseGrid briefing a field volunteer. Output ONLY a concise operational paragraph — no title, no bullets, no JSON.

CRITICAL RULES:
- Do NOT invent equipment, vehicles, or permissions. Do NOT change assignment or priority decisions.
- Action-oriented, calm, brief (mobile task view).
- {_language_instruction(lang)}

Structured facts:
- volunteer_id: {volunteer_id}
- volunteer_display_name: {vol.get("display_name", "")}
- volunteer_skills_or_types: {vskills}
- volunteer_support_types: {vsupport}
- volunteer_transport_access: {vol.get("transport_access", "")}
- incident_type: {inc.get("incident_type", "")}
- status: {inc.get("status", "")}
- severity: {inc.get("severity", "")}
- priority_label: {inc.get("priority_label", "")}
- zone_id: {inc.get("zone_id", "")}
- people_count: {inc.get("people_count", "")}
- key_need_flags: {flag_line}
- route_status: {inc.get("route_status", "")}
- note_excerpt: {(str(inc.get("note") or "")[:240])}

Write 3–5 sentences: what to verify before moving, what to prioritize on scene, what to avoid.
"""


def _build_coordinator_prompt(ctx: dict[str, Any]) -> str:
    inc = ctx["incident"]
    rep = ctx.get("reporter") or {}
    vol = ctx.get("volunteer") or {}
    lang = "en"
    flags = []
    for key, label in (
        ("elderly", "elderly"),
        ("child_present", "child"),
        ("injury", "injury"),
        ("oxygen_required", "oxygen"),
        ("shelter_needed", "shelter"),
        ("food_needed", "food"),
        ("transport_needed", "transport"),
    ):
        if inc.get(key):
            flags.append(label)
    profile_bits = []
    if rep.get("household_size") is not None or rep.get("family_size") is not None:
        profile_bits.append(f"household_size={rep.get('household_size') or rep.get('family_size')}")
    if rep.get("oxygen_dependency"):
        profile_bits.append("reporter_oxygen_dependency=true")
    if rep.get("mobility_concern"):
        profile_bits.append("reporter_mobility_concern=true")
    profile_line = "; ".join(profile_bits) if profile_bits else "none"

    return f"""You are PulseGrid producing a short operational triage summary for a coordinator console. Output plain text only — 4–7 sentences, professional tone, no markdown, no JSON.

CRITICAL RULES:
- Do NOT instruct the coordinator to override system priority or routing; summarize and highlight risks only.
- English only for this role unless facts indicate another coordinator locale (use English here).

Facts:
- incident_type: {inc.get("incident_type", "")}
- status: {inc.get("status", "")}
- severity: {inc.get("severity", "")}
- priority_label: {inc.get("priority_label", "")} / score: {inc.get("priority_score", "")}
- zone_id: {inc.get("zone_id", "")}
- people_count: {inc.get("people_count", "")}
- risk_flags: {", ".join(flags) if flags else "none"}
- assigned_volunteer: {vol.get("display_name") or vol.get("id") or "none"}
- route_status: {inc.get("route_status", "")}
- profile_derived: {profile_line}
- note_excerpt: {(str(inc.get("note") or "")[:280])}

Summarize the situation, key risks, and why the current assignment (if any) is directionally reasonable given zone and needs.
"""


def _try_gemini(prompt: str) -> tuple[str, bool]:
    try:
        client = get_gemini_text_client()
        text = client.generate_text(prompt=prompt)
        return text, False
    except (GeminiUnavailableError, GeminiGenerationError):
        return "", True
    except Exception:  # noqa: BLE001
        return "", True


def _generate_affected_from_ctx(ctx: dict[str, Any]) -> GuidanceResponse:
    lang = _language_from_context(ctx)
    prompt = _build_affected_prompt(ctx)
    text, fb = _try_gemini(prompt)
    if fb or not text.strip():
        text = _fallback_affected(ctx)
        fb = True
    return GuidanceResponse(role="affected_user", language=lang, message=text.strip(), fallback_used=fb, generated_at=_iso_now())


def generate_affected_user_guidance(body: AffectedUserGuidanceRequest) -> GuidanceResponse:
    ctx = _load_ai_context(incident_id=body.incident_id)
    if ctx is None:
        return GuidanceResponse(
            role="affected_user",
            language="en",
            message="We could not load this incident. Please refresh or contact support.",
            fallback_used=True,
            generated_at=_iso_now(),
        )
    return _generate_affected_from_ctx(ctx)


def generate_volunteer_guidance(body: VolunteerGuidanceRequest) -> GuidanceResponse:
    ctx = _load_ai_context(incident_id=body.incident_id)
    if ctx is None:
        return GuidanceResponse(
            role="volunteer",
            language="en",
            message="Incident not found.",
            fallback_used=True,
            generated_at=_iso_now(),
        )
    vol = ctx.get("volunteer") or {}
    vid = (body.volunteer_id or "").strip() or str(vol.get("id") or "")
    if not vid:
        return GuidanceResponse(
            role="volunteer",
            language="en",
            message=_fallback_volunteer(),
            fallback_used=True,
            generated_at=_iso_now(),
        )
    lang = _language_from_context(ctx)
    prompt = _build_volunteer_prompt(ctx, volunteer_id=vid)
    text, fb = _try_gemini(prompt)
    if fb or not text.strip():
        text = _fallback_volunteer()
        fb = True
    return GuidanceResponse(role="volunteer", language=lang, message=text.strip(), fallback_used=fb, generated_at=_iso_now())


def _generate_coordinator_from_ctx(ctx: dict[str, Any]) -> GuidanceResponse:
    prompt = _build_coordinator_prompt(ctx)
    text, fb = _try_gemini(prompt)
    if fb or not text.strip():
        text = _fallback_coordinator()
        fb = True
    return GuidanceResponse(role="coordinator", language="en", message=text.strip(), fallback_used=fb, generated_at=_iso_now())


def generate_coordinator_summary(body: CoordinatorSummaryRequest) -> GuidanceResponse:
    ctx = _load_ai_context(incident_id=body.incident_id)
    if ctx is None:
        return GuidanceResponse(
            role="coordinator",
            language="en",
            message="Incident not found.",
            fallback_used=True,
            generated_at=_iso_now(),
        )
    return _generate_coordinator_from_ctx(ctx)


def get_incident_guidance_bundle(*, incident_id: str, include_coordinator: bool = False) -> IncidentGuidanceBundleResponse | None:
    ctx = _load_ai_context(incident_id=incident_id)
    if ctx is None:
        return None
    affected = _generate_affected_from_ctx(ctx)
    coord: GuidanceResponse | None = None
    if include_coordinator:
        coord = _generate_coordinator_from_ctx(ctx)
    return IncidentGuidanceBundleResponse(incident_id=incident_id, affected_user=affected, coordinator_summary=coord)
