from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.plan import Plan, PlanItem
from app.models.user import User
from app.schemas.plan import PlanIn, PlanOut

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanOut])
def list_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Plan).filter(Plan.user_id == current_user.id).order_by(Plan.date.desc()).limit(90).all()


@router.get("/{plan_date}", response_model=PlanOut)
def get_plan(plan_date: date, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.date == plan_date).first()
    if not plan:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Plan not found"})
    return plan


@router.post("", response_model=PlanOut)
def upsert_plan(payload: PlanIn, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    plan = db.query(Plan).filter(Plan.user_id == current_user.id, Plan.date == payload.date).first()
    if not plan:
        plan = Plan(user_id=current_user.id, date=payload.date, reflection=payload.reflection)
        db.add(plan)
        db.flush()
    else:
        plan.reflection = payload.reflection
        db.query(PlanItem).filter(PlanItem.plan_id == plan.id).delete()

    for item in payload.items:
        db.add(
            PlanItem(
                plan_id=plan.id,
                title=item.title,
                status=item.status,
                estimate_minutes=item.estimate_minutes,
                tags=item.tags,
            )
        )

    db.commit()
    db.refresh(plan)
    return plan


@router.patch("/item/{item_id}/status")
def update_item_status(item_id: str, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = (
        db.query(PlanItem)
        .join(Plan, Plan.id == PlanItem.plan_id)
        .filter(PlanItem.id == item_id, Plan.user_id == current_user.id)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Plan item not found"})

    item.status = status
    db.add(item)
    db.commit()
    return {"status": "ok"}
