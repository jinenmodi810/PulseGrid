from pydantic import BaseModel, Field


class AssignmentResultRead(BaseModel):
    incident_id: str
    assigned_resource_id: str
    accepted: bool
    rejection_reasons: list[str] = Field(default_factory=list)
