"""Read model for affected-user profile (Neo4j User)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class UserProfileResponse(BaseModel):
    user_id: str
    email: str = ""
    full_name: str = ""
    phone: str = ""
    preferred_language: str = "en"
    zone_id: str = ""
    household_size: int = 1
    elderly_count: int = 0
    mobility_concern: bool = False
    oxygen_dependency: bool = False
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    emergency_contact_relationship: str = ""
