from celery import Celery

from app.core.config import settings

celery_app = Celery("lifepause", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task
def send_break_notification(user_id: str):
    return {"status": "queued", "user_id": user_id, "channel": "web_push_stub"}
