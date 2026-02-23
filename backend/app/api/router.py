from fastapi import APIRouter

from app.api.v1 import auth, checkins, insights, notifications, org, plans, sessions, settings, system, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(system.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(sessions.router)
api_router.include_router(plans.router)
api_router.include_router(checkins.router)
api_router.include_router(settings.router)
api_router.include_router(insights.router)
api_router.include_router(notifications.router)
api_router.include_router(org.router)
