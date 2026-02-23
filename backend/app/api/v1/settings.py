from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.break_rule import BreakRule
from app.models.user import User
from app.schemas.break_rule import BreakRuleIn, BreakRuleOut
from app.services.breaks import adaptive_rule_adjustment

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/break-rule", response_model=BreakRuleOut)
def get_break_rule(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(BreakRule).filter(BreakRule.user_id == current_user.id).first()


@router.put("/break-rule", response_model=BreakRuleOut)
def update_break_rule(payload: BreakRuleIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rule = db.query(BreakRule).filter(BreakRule.user_id == current_user.id).first()
    if not rule:
        rule = BreakRule(user_id=current_user.id, **payload.model_dump())
    else:
        for key, value in payload.model_dump().items():
            setattr(rule, key, value)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/break-rule/adaptive")
def adaptive_break_preview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rule = db.query(BreakRule).filter(BreakRule.user_id == current_user.id).first()
    if not rule:
        rule = BreakRule(user_id=current_user.id)
        db.add(rule)
        db.commit()
        db.refresh(rule)
    return adaptive_rule_adjustment(db, current_user.id, rule.focus_min, rule.break_min)
