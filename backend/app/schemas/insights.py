from pydantic import BaseModel


class InsightPoint(BaseModel):
    label: str
    value: float


class InsightsOut(BaseModel):
    energy_balance_score: float
    weekly_work_vs_stress: list[InsightPoint]
    top_tags: list[InsightPoint]
    break_compliance: float
    recommendations: list[str]
