from pydantic import BaseModel


class ShelterRead(BaseModel):
    id: str
    name: str
    capacity: int = 0
    occupancy: int = 0
    latitude: float | None = None
    longitude: float | None = None
