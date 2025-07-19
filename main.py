from fastapi import FastAPI
from app.routers import report_router
from app.services.scheduler_service import start_scheduler
from app.routers import admin_router
from fastapi import Request
from time import time
from app.core import metrics
from fastapi import APIRouter
from app.core.metrics import get_metrics

metrics_router = APIRouter()

@metrics_router.get("/metrics")
def metrics_endpoint():
    return get_metrics()


# 👈 import your metrics module
start_scheduler()

app = FastAPI()
app.include_router(report_router.router)

app.include_router(admin_router.router)

app.include_router(metrics_router)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time()
    response = await call_next(request)
    duration = (time() - start) * 1000
    metrics.track_metrics(request, duration)
    return response
@app.get("/")
def read_root():
    return {"message": "AI Backend Developer Test API running 🚀"}
