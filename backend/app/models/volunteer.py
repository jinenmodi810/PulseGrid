from pydantic import BaseModel, Field


class VolunteerRead(BaseModel):
    id: str
    display_name: str
    skills: list[str] = Field(default_factory=list)
    credits: int = 0
    trust_score: float = Field(default=0.5, ge=0, le=1)
    zone_id: str = ""
    skill_type: str = ""
    support_types: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    transport_access: str = ""
    availability: str = ""
