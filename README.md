# LifePause

LifePause is an anti-burnout personal rhythm system with B2C and optional B2B analytics mode.

## 1) Product Plan

### Phase 1: MVP (B2C core)
- Auth: signup/login/refresh/reset-stub, profile.
- Time tracking: start/stop + manual sessions + tagging.
- Daily plans: top priorities + plan item statuses + reflection.
- Daily check-ins: energy/stress/mood/sleep + notes + streak.
- Smart breaks: configurable break rules + adaptive heuristic + notification logs.
- Insights: energy balance score, weekly trends, top tags, rule-based recommendations.
- Landing + app shell UX.

### Phase 2: Premium
- Feature-flag gated deeper analytics endpoint.
- AI recommendations integration interface (stub endpoint in backend).
- Personalized scheduling and richer correlations.

### Phase 3: B2B
- Organizations, members, RBAC (org_admin/hr_viewer/member).
- Privacy-safe aggregate dashboard only.
- CSV/PDF report exports.
- Corporate subscription workflow integration points.

## 2) Monorepo Layout

- `frontend/`: Next.js 15 App Router + TypeScript + Tailwind + Zustand + React Query
- `backend/`: FastAPI + SQLAlchemy + Alembic + JWT
- `infra/`: Docker Compose + Nginx reverse proxy config

## 3) Local Setup

### Prerequisites
- Docker + Docker Compose
- (Optional local dev) Python 3.12+, Node 22+

### Quick start with Docker
1. `cd infra`
2. `docker compose up --build`
3. Open:
- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

### Seed demo data
1. `docker compose exec backend python scripts/seed.py`
2. Demo user: `demo@lifepause.app` / `Demo1234!`

## 4) Backend (without Docker)

1. `cd backend`
2. `python -m venv .venv && .venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and adjust values.
5. `alembic upgrade head`
6. `uvicorn app.main:app --reload`

## 5) Frontend (without Docker)

1. `cd frontend`
2. `npm install`
3. Copy `.env.example` to `.env.local`
4. `npm run dev`

## 6) Migrations

- Apply migrations: `cd backend && alembic upgrade head`
- Create new migration: `alembic revision --autogenerate -m "message"`

## 7) Tests

### Backend
- `cd backend && pytest`

### Frontend
- `cd frontend && npm test`

## 8) VPS Deploy Guide (production)

1. Provision Ubuntu VPS with Docker.
2. Clone repo and set production env vars (`SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, `NEXT_PUBLIC_API_URL`).
3. Use managed Postgres/Redis or dedicated containers.
4. Build and start services from `infra/docker-compose.yml`.
5. Put Nginx in front using `infra/nginx/lifepause.conf`, configure TLS via Let's Encrypt.
6. Run `alembic upgrade head` and `python scripts/seed.py` only for non-prod/demo environments.
7. Set up monitoring (Prometheus/Grafana) and centralized logs.

## 9) Notes

- Password hashing uses bcrypt via passlib.
- Auth endpoints include basic in-memory rate limiting.
- Org analytics are aggregate-only to avoid individual drill-down privacy risk.
- Web push/email are integration stubs with notification logs.
- Celery + Redis worker included for async upgrade path.

## 10) Acceptance Criteria Checklist

- [x] MVP auth, profile, reset stub.
- [x] Time tracking (active/manual/edit/list).
- [x] Daily plans and plan items.
- [x] Daily check-ins + streak endpoint.
- [x] Smart break rule config + adaptive heuristic + notifications log/snooze.
- [x] Insights dashboard API with energy balance + trends + tips.
- [x] Premium stubs (deep analytics + AI recommendations interface).
- [x] B2B org model, RBAC checks, aggregate dashboard, CSV/PDF exports.
- [x] Alembic migration and seed script.
- [x] Minimal tests for auth/sessions/check-ins + frontend smoke test.
- [x] Dockerized local and production-oriented setup docs.
