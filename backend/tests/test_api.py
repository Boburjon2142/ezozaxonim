from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.db.session import Base, SessionLocal, engine
from app.main import app
from app.models.user import User


client = TestClient(app)


def setup_module():
    Base.metadata.create_all(bind=engine)


def _cleanup_user(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()


def test_auth_signup_and_login():
    email = "test_auth@lifepause.app"
    _cleanup_user(email)

    signup = client.post("/api/v1/auth/signup", json={"email": email, "password": "Test1234!", "full_name": "Test User"})
    assert signup.status_code == 200
    assert "access_token" in signup.json()

    login = client.post("/api/v1/auth/login", json={"email": email, "password": "Test1234!"})
    assert login.status_code == 200
    assert "refresh_token" in login.json()


def test_time_session_flow():
    email = "test_session@lifepause.app"
    _cleanup_user(email)
    token = client.post("/api/v1/auth/signup", json={"email": email, "password": "Test1234!", "full_name": "Timer User"}).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    start = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
    end = datetime.utcnow().isoformat()

    create = client.post("/api/v1/sessions", json={"started_at": start, "ended_at": end, "tags": "deep-work"}, headers=headers)
    assert create.status_code == 200
    assert create.json()["duration_minutes"] >= 29

    listing = client.get("/api/v1/sessions", headers=headers)
    assert listing.status_code == 200
    assert len(listing.json()) >= 1


def test_checkin_upsert():
    email = "test_checkin@lifepause.app"
    _cleanup_user(email)
    token = client.post("/api/v1/auth/signup", json={"email": email, "password": "Test1234!", "full_name": "Checkin User"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"date": "2026-02-22", "energy": 4, "stress": 2, "mood": 4, "sleep": 3, "note": "ok"}
    res1 = client.post("/api/v1/checkins", json=payload, headers=headers)
    assert res1.status_code == 200

    payload["stress"] = 3
    res2 = client.post("/api/v1/checkins", json=payload, headers=headers)
    assert res2.status_code == 200
    assert res2.json()["stress"] == 3
