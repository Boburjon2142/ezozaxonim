from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.insights import InsightPoint, InsightsOut
from app.services.insights import compute_energy_balance_score, rule_based_recommendations, weekly_trends

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("", response_model=InsightsOut)
def get_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    score = compute_energy_balance_score(db, current_user.id, date.today())
    weekly, top_tags, compliance = weekly_trends(db, current_user.id)
    recommendations = rule_based_recommendations(score, compliance)
    return InsightsOut(
        energy_balance_score=score,
        weekly_work_vs_stress=[InsightPoint(**p) for p in weekly],
        top_tags=[InsightPoint(**p) for p in top_tags],
        break_compliance=compliance,
        recommendations=recommendations,
    )


@router.get("/premium")
def premium_deep_insights_stub(current_user: User = Depends(get_current_user)):
    if not current_user.is_premium:
        return {"enabled": False, "message": "Upgrade to premium for deep analytics"}
    return {
        "enabled": True,
        "correlation": {"stress_vs_hours": -0.38},
        "personalized_schedule": ["Deep work: 09:30-11:30", "Admin: 14:00-15:00"],
    }


@router.post("/ai-recommendations")
def ai_recommendation_stub(current_user: User = Depends(get_current_user)):
    return {
        "provider": "placeholder",
        "message": "AI provider not configured. This endpoint is a production integration point.",
        "tips": ["Take a 10-minute walking break", "Split your largest task into two focus blocks"],
    }
