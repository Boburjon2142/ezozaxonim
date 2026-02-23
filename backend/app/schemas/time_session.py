from datetime import datetime
from pydantic import BaseModel


class TimeSessionIn(BaseModel):
    started_at: datetime
    ended_at: datetime | None = None
    tags: str = ""
    plan_item_id: str | None = None


class TimeSessionUpdate(BaseModel):
    started_at: datetime | None = None
    ended_at: datetime | None = None
    tags: str | None = None
    plan_item_id: str | None = None


class TimeSessionOut(BaseModel):
    id: str
    started_at: datetime
    ended_at: datetime | None
    duration_minutes: int
    tags: str
    plan_item_id: str | None

    class Config:
        from_attributes = True
