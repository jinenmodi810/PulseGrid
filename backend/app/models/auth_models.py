"""Auth token and /auth/me response models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Literal["victim", "volunteer", "organization"]
    id: str = Field(description="Canonical account id (UUID string); same value is used in Neo4j :User/:Volunteer id")


class AuthMeResponse(BaseModel):
    """Flattened profile for the signed-in principal (role-specific fields may be null)."""

    role: Literal["victim", "volunteer", "organization"]
    id: str
    email: str
    # Victim (+ optional volunteer overlap)
    full_name: str | None = None
    phone: str | None = None
    preferred_language: str | None = None
    zone_id: str | None = None
    household_size: int | None = None
    elderly_count: int | None = None
    mobility_concern: bool | None = None
    oxygen_dependency: bool | None = None
    emergency_contact_name: str | None = None
    emergency_contact_phone: str | None = None
    emergency_contact_relationship: str | None = None
    # Volunteer
    skills: list[str] | None = None
    support_types: list[str] | None = None
    languages: list[str] | None = None
    transport_access: str | None = None
    availability: str | None = None
    credits: int | None = None
    trust_score: float | None = None
    # Organization
    organization_name: str | None = None
    org_type: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    beds_available: int | None = None
    oxygen_units: int | None = None
    ambulances_available: int | None = None
    shelter_units: int | None = None
    food_capacity_units: int | None = None
    rescue_units: int | None = None
    active: bool | None = None
