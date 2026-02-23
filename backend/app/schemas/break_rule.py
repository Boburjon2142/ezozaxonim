from pydantic import BaseModel


class BreakRuleIn(BaseModel):
    focus_min: int = 25
    break_min: int = 5
    long_break_min: int = 15
    long_break_every: int = 4
    adaptive_enabled: bool = True


class BreakRuleOut(BreakRuleIn):
    id: str

    class Config:
        from_attributes = True
