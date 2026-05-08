# 7. Deployment View

## 7.1 Infrastructure Overview

Tanker24 is deployed as a set of Docker containers orchestrated via Docker Compose. The application runs on a single virtual machine (`tanker24.eu`) with container images hosted on GitHub Container Registry (`ghcr.io`).

```puml
@startuml
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

Deployment_Node(vm, "tanker24.eu", "Virtual Machine (Linux)") {
    Deployment_Node(docker, "Docker Engine", "Docker Compose Runtime") {

        Container(nginx, "Reverse Proxy", "Nginx", "Terminates TLS, routes requests to frontend and backend.")
        Container(frontend_ctr, "Frontend Container", "Node.js 24 Alpine", "SvelteKit production build, serves on port 3000.")
        Container(backend_ctr, "Backend Container", "Python 3.14 Slim", "FastAPI via uvicorn, serves on port 8000.")
        Container(postgres_ctr, "PostgreSQL Container", "PostgreSQL 18", "Database server on port 5432.")
        Container(uptime_ctr, "Uptime Kuma Container", "Uptime Kuma 2", "Monitoring dashboard on port 3001.")
    }
}

Deployment_Node(ghcr, "GitHub Container Registry", "ghcr.io") {
    Container(ghcr_backend, "Backend Image", "ghcr.io/SQS-THRO/backend:latest")
    Container(ghcr_frontend, "Frontend Image", "ghcr.io/SQS-THRO/frontend:latest")
}

Deployment_Node(gh_actions, "GitHub Actions", "CI/CD") {
    Container(build_pipeline, "Build Pipeline", ".github/workflows")
}

Rel(gh_actions, ghcr, "Pushes container images")
Rel(nginx, frontend_ctr, "Proxies / to frontend:3000")
Rel(nginx, backend_ctr, "Proxies /api to backend:8000")
Rel(backend_ctr, postgres_ctr, "SQL on port 5432")
Rel(backend_ctr, ghcr_backend, "Pulled from")
Rel(frontend_ctr, ghcr_frontend, "Pulled from")
@enduml
```

## 7.2 Container Architecture

### 7.2.1 Docker Compose Services

The `compose.yaml` at the project root defines four services:

| Service | Image / Build | Port | Purpose |
|---|---|---|---|
| `backend` | Built from `backend/Containerfile` | 8000 | FastAPI REST API |
| `frontend` | Built from `frontend/Dockerfile` | 3000 | SvelteKit web UI |
| `postgres` | `postgres:18` | 5432 | Relational database |
| `uptime-kuma` | `louislam/uptime-kuma:2` | 3001 | Health monitoring |

### 7.2.2 Backend Container (Containerfile)

```
FROM python:3.14-slim
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY ./ .
RUN uv pip install --system --no-cache .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- **Base image:** `python:3.14-slim` (minimal footprint)
- **Package manager:** `uv` (fast pip replacement from Astral)
- **Runtime:** Uvicorn ASGI server with single worker
- **Configuration:** All settings passed via `.env` file (mounted by Docker Compose)

### 7.2.3 Frontend Container (Dockerfile)

Multi-stage build:

```
Stage 1 (build):
  FROM node:24-alpine
  npm ci → npm run build → npm prune --omit=dev

Stage 2 (production):
  FROM node:24-alpine
  COPY build/, node_modules/, package.json
  EXPOSE 3000
  CMD ["node", "build"]
```

- **Build stage:** Compiles SvelteKit with Vite, prunes dev dependencies
- **Runtime stage:** Minimal Node.js Alpine image, only production code
- **Output:** Node.js server running the compiled SvelteKit application

### 7.2.4 Database Initialization

The PostgreSQL container is started with a health check (`pg_isready`) before the backend starts:

```yaml
depends_on:
  postgres:
    condition: service_healthy
```

Table creation is handled at backend startup via SQLAlchemy's `Base.metadata.create_all()` — no migration tool is used.

## 7.3 Persistent Volumes

| Volume | Mount Point | Purpose |
|---|---|---|
| `postgres_data` | `/var/lib/postgresql` | PostgreSQL data files (user accounts, cars, history, station cache) |
| `uptime_kuma_data` | `/app/data` | Uptime Kuma monitoring configuration and history |

## 7.4 CI/CD Pipeline

The continuous delivery pipeline is implemented with GitHub Actions and consists of three stages:

### 7.4.1 Stage 1: Build and Test

```
.github/workflows/test_backend.yml    → Runs on push to main / PR
  - test:   Python 3.14, uv install, pytest --cov
  - lint:   Ruff check + Ruff format
  - typecheck: mypy app/

.github/workflows/test_frontend.yml   → Runs on push to main / PR
  - test: Node.js 24, npm install, vitest run
  - lint: ESLint + Prettier
  - e2e:  Playwright (chromium)
```

### 7.4.2 Stage 2: Build and Push Images

```
.github/workflows/build_backend.yml   → Triggered on push to main (backend/**)
  - Build Docker image (Containerfile)
  - Push to ghcr.io/SQS-THRO/backend:latest

.github/workflows/build_frontend.yml  → Triggered on push to main (frontend/**)
  - Build Docker image (Dockerfile)
  - Push to ghcr.io/SQS-THRO/frontend:latest
```

### 7.4.3 Stage 3: Deploy

```
.github/workflows/deploy.yml          → Triggered after builds complete or on release/push to main
  - SSH into tanker24.eu
  - Execute /usr/bin/redeploy script (docker compose pull + up -d)
```

### 7.4.4 Quality Gate

```
.github/workflows/sonarcloud.yml      → Runs on push to main / PR
  - Backend: pytest --cov → coverage.xml
  - Frontend: vitest --coverage → lcov.info
  - SonarCloud scan: static analysis, coverage, quality gate
```

Only releases trigger automatic deployment by default. The push-to-main trigger is disabled via comments in the workflow file.

## 7.5 Environment Configuration

The application uses a `.env` file (not committed) for all configuration. Key variables:

| Variable | Purpose | Example |
|---|---|---|
| `SECRET` | JWT signing key | Random string |
| `DB_TYPE` | Database backend | `postgresql` or `sqlite` |
| `POSTGRES_USER/PASSWORD/DB/HOST/PORT` | PostgreSQL connection | Credentials |
| `TANKERKOENIG_API_KEY` | API key for Tankerkönig | UUID |
| `INVITATION_KEYS` | Comma-separated 32-char hex keys | `901563b82fa7adcbbc2a7e885f143c57,...` |
| `CORS_ORIGINS` | Allowed frontend origins | `https://tanker24.eu` |
| `NEARBY_STATIONS_RATE_LIMIT` | Per-user rate limit | `10/minute` |
| `PUBLIC_BACKEND_URL` | Backend URL (for frontend) | `https://tanker24.eu/api` |

A template file `.env.example` is provided for new deployments.

## 7.6 Network Topology

```
                    Internet
                        │
                        ▼
              ┌─────────────────┐
              │  Nginx (TLS)    │
              │  Port 443       │
              └───┬─────────┬───┘
                  │         │
       /          ▼         ▼     /api
    ┌──────────┐       ┌──────────┐
    │ Frontend │       │ Backend  │
    │  :3000   │──────▶│  :8000   │
    └──────────┘       └────┬─────┘
                            │
      ┌─────────────────────┤
      │                     │
      ▼                     ▼
┌──────────┐         ┌──────────────┐
│PostgreSQL│         │ Tankerkönig  │
│  :5432   │         │  API (ext)   │
└──────────┘         └──────────────┘

┌─────────────┐
│ Uptime Kuma │  ← Internal monitoring (port 3001)
└─────────────┘
```

- Nginx handles TLS termination and reverse proxying.
- The frontend communicates with the backend through the proxy (same-origin deployment) or via direct REST calls (in development).
- PostgreSQL is only accessible from the backend container (internal Docker network).
- Uptime Kuma polls the health endpoints of frontend and backend for monitoring.