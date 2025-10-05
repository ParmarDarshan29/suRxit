# suRxit Gateway Service

## Overview
Central API gateway for suRxit, orchestrating OCR, NER, FeatureGen, Risk-Engine, Alerts, and User Management.

## Endpoints
- `/analyze/prescription` — Full pipeline (OCR → NER → Risk-Engine)
- `/risk/*` — Proxy to Risk-Engine
- `/patient/*` — CRUD for patients, history, allergies
- `/alerts/*` — Fetch triggered alerts
- `/health` — Health check & Prometheus metrics

## Background Jobs
- Kafka/Redis subscriber for `RISK_ALERT` events
- Dispatches alerts to DB and notifies users

## Security
- JWT Auth with RBAC (doctor, patient, admin)
- API-keys for internal ML-services

## Data
- Postgres: patients, prescriptions, alerts, audit_log, dfi_cache, home_remedy_cache
- Redis: recent KG/DFI lookups

## Running
```bash
docker build -t gateway .
docker run -p 8000:8000 gateway
```

## Testing
```bash
pytest tests/
```
