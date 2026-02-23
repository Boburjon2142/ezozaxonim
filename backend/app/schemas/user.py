from pydantic import BaseModel


class UserProfileOut(BaseModel):
    id: str
    email: str
    full_name: str
    timezone: str
    preferred_work_hours: str
    goals: str
    push_enabled: bool
    is_premium: bool

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    timezone: str | None = None
    preferred_work_hours: str | None = None
    goals: str | None = None
    push_enabled: bool | None = None
