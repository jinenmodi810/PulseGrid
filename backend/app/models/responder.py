from pydantic import BaseModel


class ResponderRead(BaseModel):
    id: str
    unit_name: str
    role: str
    status: str
