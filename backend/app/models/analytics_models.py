"""Analytics API response models."""

from __future__ import annotations

from pydantic import BaseModel


class AnalyticsOverviewSection(BaseModel):
    incidents_total: int | None = None
    avg_time_to_assignment_seconds: float | None = None
    avg_time_to_completion_seconds: float | None = None
    volunteers_total: int | None = None
    tasks_assigned_total: int | None = None
    tasks_completed_total: int | None = None
    organizations_total: int | None = None
    beds_available_total: int | None = None


class AnalyticsOverviewResponse(BaseModel):
    incident_operations: dict
    volunteer_performance: dict
    organization_capacity: dict


class IncidentByZoneItem(BaseModel):
    zone_id: str | None = None
    incidents: int = 0


class VolunteerPerformanceItem(BaseModel):
    volunteer_id: str
    tasks_assigned: int = 0
    tasks_accepted: int = 0
    tasks_completed: int = 0
    latest_credits: int | None = None
    latest_trust_score: float | None = None
    avg_completion_time_seconds: float | None = None


class OrganizationCapacityItem(BaseModel):
    organization_id: str
    captured_at: str | None = None
    beds_available: int | None = None
    oxygen_units: int | None = None
    ambulances_available: int | None = None
    shelter_units: int | None = None
    food_capacity_units: int | None = None
    rescue_units: int | None = None


class TimeToResponseResponse(BaseModel):
    avg_time_to_assignment_seconds: float | None = None
    avg_time_to_acceptance_seconds: float | None = None
    avg_time_to_completion_seconds: float | None = None
