from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "lifepause-api"}


@router.get("/metrics")
def metrics_stub():
    return {"metrics": "stub", "message": "Prometheus integration pending"}
