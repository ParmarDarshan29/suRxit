from fastapi import FastAPI
from routers import analyze, risk, alerts, patient
from auth import setup_auth
from prometheus_client import make_asgi_app

app = FastAPI(title="suRxit Gateway API")
setup_auth(app)

app.include_router(analyze.router, prefix="/analyze")
app.include_router(risk.router, prefix="/risk")
app.include_router(alerts.router, prefix="/alerts")
app.include_router(patient.router, prefix="/patient")

# Prometheus metrics and health
app.mount("/health", make_asgi_app())
