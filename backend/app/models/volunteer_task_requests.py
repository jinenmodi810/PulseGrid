"""Volunteer task feed and lifecycle API contracts."""

from __future__ import annotations

from pydantic import BaseModel, Field


class VolunteerIdBody(BaseModel):
    volunteer_id: str = Field(..., min_length=1)


class VolunteerTaskItem(BaseModel):
    incident_id: str
    incident_type: str
    priority_label: str
    priority_score: float = 0
    zone_id: str = ""
    status: str = "open"
    note: str = ""
    eta_minutes: int | None = None
    route_status: str = "pending"
    shelter_needed: bool = False
    food_needed: bool = False
    transport_needed: bool = False
    elderly: bool = False
    child_present: bool = False
    injury: bool = False
    oxygen_required: bool = False
    task_source: str = Field(default="assigned", description="assigned | nearby_open")
    response_tier: str = ""
    decision_summary: str = ""


class AcceptTaskResponse(BaseModel):
    incident_id: str
    status: str
    priority_label: str = ""
    zone_id: str = ""


class VolunteerRewardSnapshot(BaseModel):
    volunteer_id: str
    credits: int = 0
    trust_score: float = 0.5


class CompleteTaskResponse(BaseModel):
    incident_id: str
    status: str
    volunteer: VolunteerRewardSnapshot


class ReassignRequest(BaseModel):
    new_volunteer_id: str = Field(..., min_length=1)


class CoordinatorNoteRequest(BaseModel):
    note: str = Field(default="", max_length=2000)


class CoordinatorIncidentActionResponse(BaseModel):
    incident_id: str
    status: str
    route_status: str | None = None
