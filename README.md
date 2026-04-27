# PulseGrid

PulseGrid is a multi-role crisis coordination platform with:

- Flutter client app (Affected User, Volunteer, Organization, Admin inspection)
- FastAPI backend (auth, incidents, organizations, realtime, analytics)
- Event-driven data platform (Outbox -> Kafka/Redpanda -> Bronze/Silver/Gold -> Analytics API)

This repository is structured so anyone can quickly fork, run locally, and start building.

---

## Table of Contents

- [What This Project Does](#what-this-project-does)
- [Architecture at a Glance](#architecture-at-a-glance)
- [Core User Flows](#core-user-flows)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Fastest Path)](#quick-start-fastest-path)
- [Environment Configuration](#environment-configuration)
- [Run the Flutter App](#run-the-flutter-app)
- [Run the Backend API](#run-the-backend-api)
- [Run the Data Platform Pipeline](#run-the-data-platform-pipeline)
- [API Overview](#api-overview)
- [Realtime (WebSocket) Channels](#realtime-websocket-channels)
- [Testing](#testing)
- [Production Hardening Checklist](#production-hardening-checklist)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## What This Project Does

PulseGrid coordinates emergency response across multiple actors:

1. Affected user submits a help request (incident).
2. System computes priority and matching.
3. Volunteers receive and execute tasks.
4. Organizations monitor incidents and capacity.
5. Events feed an analytics pipeline for KPI dashboards.

PulseGrid combines:

- Operational workflows (REST + realtime updates)
- Analytics workflows (event-driven medallion data pipeline)

---

## Architecture at a Glance

```text
Flutter App
   |
   v
FastAPI Backend
   |---------------------> Neo4j (graph workflows, matching/traversal)
   |
   |---------------------> PostgreSQL (system-of-record + outbox)
                               |
                               v
                        Outbox Publisher
                               |
                               v
                        Kafka/Redpanda
                               |
                               v
                     Bronze (MinIO/S3 raw events)
                               |
                               v
                     Silver ETL (normalized parquet)
                               |
                               v
                     Gold ETL (business marts)
                               |
                               v
               Analytics API (DuckDB over Gold parquet)
```

---

## Core User Flows

### Affected User

- Register/login
- Submit incident request
- Track incident status and guidance

### Volunteer

- Register/login
- View assigned/nearby tasks
- Accept and complete tasks
- Receive credits/trust updates

### Organization

- Register/login
- View organization overview and incidents
- Update resource capacity
- Update response status
- Access analytics endpoints

### Realtime

- Dashboard and role-specific views refresh over WebSocket channels

---

## Tech Stack

### Frontend

- Flutter
- Riverpod
- GoRouter
- Dio
- web_socket_channel

### Backend

- FastAPI
- SQLAlchemy + Alembic
- Neo4j Python driver
- JWT + bcrypt

### Data Platform

- Redpanda/Kafka
- MinIO (S3-compatible)
- Pandas + PyArrow
- DuckDB
- dbt (scaffolded)
- Dagster (scaffolded)

### Observability

- Prometheus metrics endpoint (`/metrics`)
- Runtime counters for Bronze/Silver/Gold jobs
- Lineage event output

---

## Repository Structure

```text
.
├── lib/                          # Flutter app
│   ├── app/                      # App shell, router, theme, providers
│   ├── core/                     # Shared services/utils/widgets
│   ├── data/                     # Sources/repositories/models
│   ├── domain/                   # Use cases/entities
│   └── features/                 # Role/feature modules
├── backend/
│   ├── app/
│   │   ├── api/routes/           # FastAPI routes
│   │   ├── services/             # Business/services layer
│   │   ├── db/sql/               # SQLAlchemy models/session
│   │   ├── domain/               # Event contracts/types/streaming helpers
│   │   ├── jobs/                 # Outbox/Bronze/Silver/Gold jobs
│   │   └── observability/        # Metrics/lineage
│   ├── alembic/                  # DB migrations
│   ├── data/seed/                # Seed data
│   ├── tests/                    # Unit/integration tests
│   ├── orchestration/            # Dagster defs
│   └── dbt_project/              # dbt models
├── docker-compose.yml            # Redpanda + MinIO local infra
└── Makefile                      # Helper targets
```

---

## Prerequisites

- Flutter SDK (Dart 3.11+)
- Python 3.11+
- Docker + Docker Compose
- PostgreSQL (local)
- Neo4j AuraDB or local Neo4j

---

## Quick Start (Fastest Path)

1. Clone the repository:

```bash
git clone <your-fork-url>
cd PulseGrid
```

2. Start local data infra:

```bash
docker compose up -d
```

3. Backend setup:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

4. Update `backend/.env` with your PostgreSQL/Neo4j details.

5. Run migrations + seed:

```bash
alembic upgrade head
python seed_data_loader.py
```

6. Start backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

7. Start Flutter app (new terminal):

```bash
cd ..
flutter pub get
flutter run
```

---

## Environment Configuration

Never commit real secrets or credentials.

### Root `.env` (Flutter)

- `API_BASE_URL=http://127.0.0.1:8002`
- `GEMINI_API_KEY=` (optional for client-side experiments; backend key preferred)

### `backend/.env`

Typical local keys:

```env
# Core DBs
DATABASE_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/pulsegrid_db
NEO4J_URI=neo4j+s://<your-aura-uri>
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<your-password>
NEO4J_DATABASE=neo4j

# Security
JWT_SECRET=<strong-random-secret>
ADMIN_EMAIL=<admin-email>
ADMIN_PASSWORD=<admin-password>
ADMIN_SESSION_MARKER=admin-hackathon

# Kafka/Redpanda
KAFKA_BOOTSTRAP_SERVERS=localhost:19092

# MinIO / S3-compatible
BRONZE_S3_ENDPOINT_URL=http://localhost:9000
BRONZE_S3_ACCESS_KEY=minioadmin
BRONZE_S3_SECRET_KEY=minioadmin
BRONZE_S3_REGION=us-east-1
BRONZE_S3_USE_SSL=false

# CORS (comma-separated)
CORS_ORIGINS=http://127.0.0.1:8000,http://127.0.0.1:8002,http://localhost:8000,http://localhost:8002
```

---

## Run the Flutter App

```bash
flutter pub get
flutter run
```

Notes:

- iOS simulator defaults to localhost backend.
- Android emulator uses `10.0.2.2` fallback in resolver.

---

## Run the Backend API

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8002
```

Useful endpoints:

- Health: `GET /health`
- Neo4j check: `GET /health/neo4j`
- Metrics: `GET /metrics`
- Swagger: `http://127.0.0.1:8002/docs`

---

## Run the Data Platform Pipeline

1. Start infra:

```bash
docker compose up -d
```

2. Start outbox publisher:

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python3 -m app.jobs.outbox_publisher
```

3. Run Bronze ingestion:

```bash
PYTHONPATH=. python3 -m app.jobs.bronze_ingestor
```

4. Run Silver ETL:

```bash
PYTHONPATH=. python3 -m app.jobs.silver_etl
```

5. Run Gold ETL:

```bash
PYTHONPATH=. python3 -m app.jobs.gold_etl
```

6. Query analytics:

- `GET /analytics/overview`
- `GET /analytics/incidents-by-zone`
- `GET /analytics/volunteer-performance`
- `GET /analytics/organization-capacity`
- `GET /analytics/time-to-response`

---

## API Overview

### Auth

- `POST /auth/register-victim`
- `POST /auth/login-victim`
- `POST /auth/register-volunteer`
- `POST /auth/login-volunteer`
- `POST /auth/register-organization`
- `POST /auth/login-organization`
- `GET /auth/me`

### Incidents

- `POST /incidents/preview-priority`
- `POST /incidents/`
- `GET /incidents/{incident_id}`
- `POST /incidents/{incident_id}/accept`
- `POST /incidents/{incident_id}/complete`
- `POST /incidents/{incident_id}/reassign`
- `POST /incidents/{incident_id}/escalate`
- `POST /incidents/{incident_id}/block-route`

### Organizations

- `GET /organizations/{organization_id}/overview`
- `GET /organizations/{organization_id}/incidents`
- `POST /organizations/{organization_id}/capacity-update`
- `POST /organizations/{organization_id}/accept-incident`
- `POST /organizations/{organization_id}/update-response-status`

### Analytics

- `GET /analytics/overview`
- `GET /analytics/incidents-by-zone`
- `GET /analytics/volunteer-performance`
- `GET /analytics/organization-capacity`
- `GET /analytics/time-to-response`

---

## Realtime (WebSocket) Channels

- `/ws/dashboard`
- `/ws/incidents/{incident_id}`
- `/ws/organizations/{organization_id}`
- `/ws/volunteers/{volunteer_id}`

These channels push live updates to client dashboards and role-specific views.

---

## Testing

### Flutter

```bash
flutter test
```

### Backend

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python3 -m unittest
```

Coverage includes event streaming, Bronze/Silver/Gold processing, and analytics APIs.

---

## Production Hardening Checklist

Before launch, confirm:

1. Strong `JWT_SECRET` and secret manager usage (no hardcoded secrets).
2. Restrictive CORS for production domains only.
3. HTTPS/TLS everywhere.
4. Admin auth upgraded beyond hackathon marker patterns.
5. WebSocket auth reviewed for token safety and logs.
6. Pipeline SLAs and alerting for freshness/failures.
7. Backup/restore and disaster recovery plan.
8. Least-privilege roles for DB/object store/message bus.

---

## Troubleshooting

### `PostgreSQL is not configured`

- Set `DATABASE_URL` in `backend/.env`
- Run `alembic upgrade head`

### Neo4j queries are slow or empty

- Verify `NEO4J_DATABASE` value (`neo4j` or server-default as required by your Aura setup)

### Analytics returns 503 (`Gold marts not found`)

- Run outbox -> bronze -> silver -> gold jobs in order

### Flutter cannot reach backend

- Verify backend is on `127.0.0.1:8002`
- Verify `API_BASE_URL` and emulator-specific host mapping

---

## Contributing

1. Fork repository
2. Create feature branch
3. Add tests with your changes
4. Run lint/tests
5. Open PR with:
   - problem statement
   - approach
   - validation steps

If this project helps you, consider starring the repository.

