from datetime import date, datetime, timedelta
from collections import Counter

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.checkin import CheckIn
from app.models.notification import NotificationLog
from app.models.time_session import TimeSession


def compute_energy_balance_score(db: Session, user_id: str, day: date) -> float:
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)

    focus_minutes = (
        db.query(func.coalesce(func.sum(TimeSession.duration_minutes), 0))
        .filter(TimeSession.user_id == user_id, TimeSession.started_at >= start, TimeSession.started_at < end)
        .scalar()
    )
    reminders = (
        db.query(NotificationLog)
        .filter(NotificationLog.user_id == user_id, NotificationLog.scheduled_at >= start, NotificationLog.scheduled_at < end)
        .all()
    )
    acknowledged = sum(1 for n in reminders if n.acknowledged_at)
    compliance = (acknowledged / len(reminders)) if reminders else 1.0

    checkin = db.query(CheckIn).filter(CheckIn.user_id == user_id, CheckIn.date == day).first()
    stress_penalty = checkin.stress * 5 if checkin else 10
    energy_bonus = checkin.energy * 4 if checkin else 10

    raw = min(100, max(0, (focus_minutes / 6) * 0.4 + compliance * 30 + energy_bonus - stress_penalty))
    return round(raw, 2)


def weekly_trends(db: Session, user_id: str) -> tuple[list[dict], list[dict], float]:
    today = date.today()
    points = []
    tag_counter = Counter()

    reminders = db.query(NotificationLog).filter(NotificationLog.user_id == user_id).all()
    compliance = (sum(1 for n in reminders if n.acknowledged_at) / len(reminders)) if reminders else 1.0

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)
        minutes = (
            db.query(func.coalesce(func.sum(TimeSession.duration_minutes), 0))
            .filter(TimeSession.user_id == user_id, TimeSession.started_at >= start, TimeSession.started_at < end)
            .scalar()
        )
        sessions = db.query(TimeSession).filter(TimeSession.user_id == user_id, TimeSession.started_at >= start, TimeSession.started_at < end).all()
        for s in sessions:
            for tag in [t.strip() for t in (s.tags or "").split(",") if t.strip()]:
                tag_counter[tag] += 1

        checkin = db.query(CheckIn).filter(CheckIn.user_id == user_id, CheckIn.date == day).first()
        stress = float(checkin.stress) if checkin else 3.0
        points.append({"label": day.isoformat(), "value": round((minutes / 60) - stress, 2)})

    tags = [{"label": k, "value": float(v)} for k, v in tag_counter.most_common(5)]
    return points, tags, round(compliance * 100, 2)


def rule_based_recommendations(score: float, break_compliance: float) -> list[str]:
    recs = []
    if break_compliance < 60:
        recs.append("Break compliance is low. Try shorter focus blocks (20-25 min).")
    if score < 50:
        recs.append("Energy balance is low. Schedule at least one 20-minute reset break daily.")
    if score >= 75:
        recs.append("Rhythm looks stable. Keep consistent start and stop hours this week.")
    if not recs:
        recs.append("Add one quick check-in after lunch to improve recommendation quality.")
    return recs
