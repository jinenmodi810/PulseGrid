from pydantic import BaseModel


class RewardRead(BaseModel):
    id: str
    title: str
    description: str
    badge_type: str
    credits_value: int = 0
