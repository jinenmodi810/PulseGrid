"""Pydantic models for lightweight hackathon auth."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class RegisterVolunteerRequest(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=3, max_length=40)
    languages: list[str] = Field(default_factory=list)
    zone_id: str = Field(..., min_length=1, max_length=120)
    availability: str = Field(default="", max_length=500)
    transport_access: str = Field(..., max_length=80)
    skills: list[str] = Field(default_factory=list)
    support_types: list[str] = Field(default_factory=list)
    verified: bool = False
    # Legacy single skill — merged into skills when skills is empty.
    skill_type: str = Field(default="", max_length=120)

    @model_validator(mode="after")
    def _skills_fallback(self) -> RegisterVolunteerRequest:
        if not self.skills and (self.skill_type or "").strip():
            object.__setattr__(self, "skills", [self.skill_type.strip()])
        return self

    @field_validator("languages", mode="before")
    @classmethod
    def _normalize_languages(cls, v: object) -> list[str]:
        if v is None:
            return ["en"]
        if isinstance(v, list):
            out = [str(x).strip() for x in v if str(x).strip()]
            return out if out else ["en"]
        s = str(v).strip()
        return [s] if s else ["en"]


class RegisterVolunteerResponse(BaseModel):
    volunteer_id: str
    zone_id: str


class RegisterOrganizationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    org_type: str = Field(..., min_length=1, max_length=80)
    phone: str = Field(default="", max_length=40)
    zone_id: str = Field(..., min_length=1, max_length=120)
    beds_available: int | None = Field(default=None, ge=0)
    oxygen_units: int | None = Field(default=None, ge=0)
    ambulances_available: int | None = Field(default=None, ge=0)
    shelter_units: int | None = Field(default=None, ge=0)
    food_capacity_units: int | None = Field(default=None, ge=0)
    rescue_units: int | None = Field(default=None, ge=0)


class RegisterOrganizationResponse(BaseModel):
    organization_id: str
    zone_id: str


class AdminLoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=200)
    password: str = Field(..., min_length=1, max_length=4096)


class AdminLoginResponse(BaseModel):
    ok: bool
    detail: str | None = None
    # TODO(Phase1): issue signed JWT and refresh tokens instead of hackathon marker.
    session_marker: str | None = None


class DashboardSummaryResponse(BaseModel):
    active_incidents: int = 0
    available_volunteers: int = 0
    hospitals_available: int = 0
    shelters_available: int = 0
    pending_requests: int = 0
    resolved_requests: int = 0


# --- MVP email/password auth ---


class RegisterVictimAuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=4096)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=3, max_length=40)
    preferred_language: str = Field(default="en", max_length=32)
    home_zone_id: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Canonical zone id from Flutter chips: zone-riverside | zone-central | zone-north | zone-east (or slug riverside, central, north, east).",
    )
    household_size: int | None = Field(default=None, ge=1, le=50)
    elderly_count: int = Field(default=0, ge=0, le=50)
    mobility_concern: bool = False
    oxygen_dependency: bool = False
    emergency_contact_name: str = Field(..., min_length=1, max_length=200)
    emergency_contact_phone: str = Field(..., min_length=3, max_length=40)
    emergency_contact_relationship: str = Field(default="", max_length=120)


class LoginVictimRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=4096)


class RegisterVolunteerAuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=4096)
    full_name: str = Field(..., min_length=1, max_length=200)
    phone: str = Field(..., min_length=3, max_length=40)
    languages: list[str] = Field(default_factory=list)
    zone_id: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Canonical zone id from Flutter: zone-riverside | zone-central | zone-north | zone-east (or slug riverside, central, north, east).",
    )
    availability: str = Field(default="", max_length=500)
    transport_access: str = Field(..., max_length=80)
    skills: list[str] = Field(default_factory=list)
    support_types: list[str] = Field(default_factory=list)
    verified: bool = False
    skill_type: str = Field(default="", max_length=120)

    @model_validator(mode="after")
    def _skills_fallback(self) -> RegisterVolunteerAuthRequest:
        if not self.skills and (self.skill_type or "").strip():
            object.__setattr__(self, "skills", [self.skill_type.strip()])
        return self

    @field_validator("languages", mode="before")
    @classmethod
    def _normalize_languages(cls, v: object) -> list[str]:
        if v is None:
            return ["en"]
        if isinstance(v, list):
            out = [str(x).strip() for x in v if str(x).strip()]
            return out if out else ["en"]
        s = str(v).strip()
        return [s] if s else ["en"]


class LoginVolunteerRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=4096)


class RegisterOrganizationAuthRequest(BaseModel):
    organization_name: str = Field(..., min_length=1, max_length=200)
    organization_type: str = Field(..., min_length=1, max_length=80)
    contact_name: str = Field(..., min_length=1, max_length=200)
    contact_phone: str = Field(..., min_length=3, max_length=40)
    contact_email: EmailStr
    password: str = Field(..., min_length=1, max_length=4096)
    zone_id: str = Field(
        ...,
        min_length=1,
        max_length=120,
        description="Canonical zone id from Flutter: zone-riverside | zone-central | zone-north | zone-east (or slug riverside, central, north, east).",
    )
    coverage_zone_ids: list[str] = Field(default_factory=list)
    beds_available: int | None = Field(default=None, ge=0)
    oxygen_units: int | None = Field(default=None, ge=0)
    ambulances_available: int | None = Field(default=None, ge=0)
    shelter_units: int | None = Field(default=None, ge=0)
    food_capacity_units: int | None = Field(default=None, ge=0)
    rescue_units: int | None = Field(default=None, ge=0)


class LoginOrganizationRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=4096)
