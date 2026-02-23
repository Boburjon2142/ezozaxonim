from pydantic import BaseModel


class OrganizationCreate(BaseModel):
    name: str


class InviteMemberRequest(BaseModel):
    email: str
    role: str = "member"


class OrgAggregateOut(BaseModel):
    avg_work_hours: float
    avg_break_compliance: float
    avg_stress: float
    burnout_risk_index: float
    team_distribution: dict[str, int]
