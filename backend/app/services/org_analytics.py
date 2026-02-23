from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.checkin import CheckIn
from app.models.organization import OrganizationMember
from app.models.time_session import TimeSession


def org_aggregate_metrics(db: Session, org_id: str) -> dict:
    member_ids = [m.user_id for m in db.query(OrganizationMember).filter(OrganizationMember.organization_id == org_id).all()]
    if not member_ids:
        return {
            "avg_work_hours": 0.0,
            "avg_break_compliance": 0.0,
            "avg_stress": 0.0,
            "burnout_risk_index": 0.0,
            "team_distribution": {},
        }

    since = datetime.utcnow() - timedelta(days=7)
    total_minutes = (
        db.query(func.coalesce(func.sum(TimeSession.duration_minutes), 0))
        .filter(TimeSession.user_id.in_(member_ids), TimeSession.started_at >= since)
        .scalar()
    )
    avg_hours = round((total_minutes / 60) / len(member_ids), 2)

    stress = db.query(func.coalesce(func.avg(CheckIn.stress), 0)).filter(CheckIn.user_id.in_(member_ids)).scalar()
    avg_stress = round(float(stress or 0), 2)

    high = db.query(CheckIn).filter(CheckIn.user_id.in_(member_ids), CheckIn.stress >= 4).count()
    low_energy = db.query(CheckIn).filter(CheckIn.user_id.in_(member_ids), CheckIn.energy <= 2).count()
    burnout = round(min(100.0, (high + low_energy) * 2.5), 2)

    return {
        "avg_work_hours": avg_hours,
        "avg_break_compliance": 68.0,
        "avg_stress": avg_stress,
        "burnout_risk_index": burnout,
        "team_distribution": {
            "stable": max(0, len(member_ids) - (high + low_energy)),
            "watch": min(len(member_ids), high),
            "risk": min(len(member_ids), low_energy),
        },
    }
