"""Pydantic contracts for admin inspection / operations API."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AdminOverviewResponse(BaseModel):
    total_users: int = 0
    total_volunteers: int = 0
    total_incidents: int = 0
    active_incidents: int = 0
    pending_incidents: int = 0
    accepted_incidents: int = 0
    resolved_incidents: int = 0
    total_hospitals: int = 0
    total_shelters: int = 0
    total_support_contacts: int = 0
    total_zones: int = 0
    total_rewards: int = 0
    total_assigned_incidents: int = 0
    total_completed_incidents: int = 0
    average_volunteer_trust_score: float = 0.0
    total_volunteer_credits: int = 0


class AdminUserItem(BaseModel):
    user_id: str
    name: str = ""
    phone: str = ""
    language: str = ""
    zone_id: str = ""
    family_size: int | None = None
    created_at: str | None = None


class AdminVolunteerItem(BaseModel):
    volunteer_id: str
    name: str = ""
    phone: str = ""
    skill_type: str = ""
    languages: list[str] = Field(default_factory=list)
    zone_id: str = ""
    availability: str = ""
    verified: bool = False
    trust_score: float = 0.0
    credits: int = 0
    assigned_incident_count: int = 0
    completed_incident_count: int = 0


class AdminIncidentItem(BaseModel):
    incident_id: str
    incident_type: str = ""
    severity: str = ""
    priority_score: float = 0.0
    priority_label: str = ""
    status: str = ""
    zone_id: str = ""
    people_count: int = 1
    created_at: str | None = None
    reported_by_user_id: str | None = None
    assigned_volunteer_id: str | None = None
    elderly: bool = False
    child_present: bool = False
    injury: bool = False
    oxygen_required: bool = False
    shelter_needed: bool = False
    food_needed: bool = False
    transport_needed: bool = False
    note: str = ""


class AdminIncidentReporter(BaseModel):
    user_id: str = ""
    name: str = ""
    phone: str = ""
    zone_id: str = ""


class AdminIncidentVolunteer(BaseModel):
    volunteer_id: str = ""
    name: str = ""
    phone: str = ""


class AdminIncidentZone(BaseModel):
    zone_id: str = ""
    name: str = ""


class AdminRejectedItem(BaseModel):
    volunteer_id: str = ""
    name: str = ""
    reason: str = ""


class AdminIncidentDetailResponse(BaseModel):
    incident: AdminIncidentItem
    reporting_user: AdminIncidentReporter | None = None
    assigned_volunteer: AdminIncidentVolunteer | None = None
    zone: AdminIncidentZone | None = None
    route_status: str = ""
    ai_guidance: str = ""
    rejected_candidates: list[AdminRejectedItem] = Field(default_factory=list)
    status_history: list[dict[str, Any]] = Field(default_factory=list)
    relationships_summary: str = ""


class AdminAssignmentItem(BaseModel):
    incident_id: str
    volunteer_id: str
    volunteer_name: str = ""
    status: str = ""
    zone_id: str = ""
    priority_label: str = ""
    assigned_at: str | None = None


class AdminRewardItem(BaseModel):
    volunteer_id: str
    volunteer_name: str = ""
    credits: int = 0
    trust_score: float = 0.0
    earned_reward_count: int = 0
    completed_incident_count: int = 0


class AdminSupportNetworkResponse(BaseModel):
    hospitals: list[dict[str, Any]] = Field(default_factory=list)
    shelters: list[dict[str, Any]] = Field(default_factory=list)
    support_contacts: list[dict[str, Any]] = Field(default_factory=list)
    zones: list[dict[str, Any]] = Field(default_factory=list)
