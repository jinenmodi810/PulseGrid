from pydantic import BaseModel


class SupportContactRead(BaseModel):
    id: str
    label: str
    phone: str
    type: str
