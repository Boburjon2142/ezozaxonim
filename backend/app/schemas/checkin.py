from datetime import date
from pydantic import BaseModel, Field


class CheckInIn(BaseModel):
    date: date
    energy: int = Field(ge=1, le=5)
    stress: int = Field(ge=1, le=5)
    mood: int = Field(ge=1, le=5)
    sleep: int = Field(ge=1, le=5)
    note: str = ""


class CheckInOut(CheckInIn):
    id: str

    class Config:
        from_attributes = True
