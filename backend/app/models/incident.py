from pydantic import BaseModel


class IncidentRead(BaseModel):
    id: str
    title: str
    status: str = "open"
    severity: str = "medium"
    created_at: str | None = None


class IncidentCreate(BaseModel):
    title: str
    status: str = "open"
    severity: str = "medium"
