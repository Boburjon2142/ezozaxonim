from datetime import date
from pydantic import BaseModel


class PlanItemIn(BaseModel):
    title: str
    status: str = "todo"
    estimate_minutes: int = 25
    tags: str = ""


class PlanItemOut(PlanItemIn):
    id: str

    class Config:
        from_attributes = True


class PlanIn(BaseModel):
    date: date
    reflection: str = ""
    items: list[PlanItemIn] = []


class PlanOut(BaseModel):
    id: str
    date: date
    reflection: str
    items: list[PlanItemOut]

    class Config:
        from_attributes = True
