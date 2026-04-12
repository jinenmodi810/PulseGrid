from pydantic import BaseModel


class HospitalRead(BaseModel):
    id: str
    name: str
    beds_available: int = 0
    latitude: float | None = None
    longitude: float | None = None
