from datetime import date, datetime, timedelta

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.break_rule import BreakRule
from app.models.checkin import CheckIn
from app.models.organization import Organization, OrganizationMember
from app.models.plan import Plan, PlanItem
from app.models.subscription import FeatureFlag, Subscription
from app.models.time_session import TimeSession
from app.models.user import User


def run() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "demo@lifepause.app").first()
        if not user:
            user = User(
                email="demo@lifepause.app",
                hashed_password=get_password_hash("Demo1234!"),
                full_name="Demo User",
                timezone="America/New_York",
                preferred_work_hours="09:00-17:30",
                goals="Sustainable focus",
                is_premium=True,
            )
            db.add(user)
            db.flush()

            db.add(BreakRule(user_id=user.id, focus_min=25, break_min=5, long_break_min=20, long_break_every=4, adaptive_enabled=True))
            db.add(Subscription(user_id=user.id, tier="premium", status="active"))
            db.add(FeatureFlag(user_id=user.id, key="premium_analytics", enabled="true"))

            org = Organization(name="Demo Org")
            db.add(org)
            db.flush()
            db.add(OrganizationMember(organization_id=org.id, user_id=user.id, role="org_admin"))

            plan = Plan(user_id=user.id, date=date.today(), reflection="Protect focus and include recovery")
            db.add(plan)
            db.flush()
            item1 = PlanItem(plan_id=plan.id, title="Ship MVP API", status="done", estimate_minutes=120, tags="backend,api")
            item2 = PlanItem(plan_id=plan.id, title="Design insights charts", status="partial", estimate_minutes=90, tags="frontend,charts")
            db.add_all([item1, item2])
            db.flush()

            now = datetime.utcnow()
            db.add_all(
                [
                    TimeSession(user_id=user.id, plan_item_id=item1.id, started_at=now - timedelta(hours=4), ended_at=now - timedelta(hours=3), duration_minutes=60, tags="backend"),
                    TimeSession(user_id=user.id, plan_item_id=item2.id, started_at=now - timedelta(hours=2), ended_at=now - timedelta(hours=1, minutes=20), duration_minutes=40, tags="frontend"),
                ]
            )

            for i in range(7):
                d = date.today() - timedelta(days=i)
                db.add(CheckIn(user_id=user.id, date=d, energy=max(1, 4 - (i % 3)), stress=min(5, 2 + (i % 3)), mood=3 + (i % 2), sleep=4 - (i % 2), note="Seeded check-in"))

        db.commit()
        print("Seed complete: demo@lifepause.app / Demo1234!")
    finally:
        db.close()


if __name__ == "__main__":
    run()
