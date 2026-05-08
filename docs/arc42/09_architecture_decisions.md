# 9. Architecture Decisions

Important architecture decisions are documented as Architecture Decision Records (ADRs). Each ADR follows a consistent template covering context, decision, rationale (with alternatives considered), and consequences.

## 9.1 ADR Overview

| ADR | Title | Decision | Status |
|---|---|---|---|
| [ADR-001](../decisions/ADR_001_FastAPI.md) | Web Framework | FastAPI | Accepted |
| [ADR-002](../decisions/ADR_002_fastapi-users.md) | Authentication Library | fastapi-users | Accepted |
| [ADR-003](../decisions/ADR_003_Svelte.md) | Frontend Framework | Svelte (SvelteKit) | Accepted |
| [ADR-004](../decisions/ADR_004_Postgresql.md) | Database | PostgreSQL 18 | Accepted |
| [ADR-005](../decisions/ADR_005_SonarQube.md) | Code Quality Analysis | SonarCloud (SonarQube) | Accepted |
| [ADR-006](../decisions/ADR_006_OpenStreetMap.md) | Map Tiles Provider | OpenStreetMap | Accepted |
| [ADR-007](../decisions/ADR_007_OSM_Standard_Tiles.md) | Tile Layer Selection | OSM Standard (light) + CartoDB Dark Matter (dark) | Accepted |
| [ADR-008](../decisions/ADR_008_TailwindCSS.md) | Styling Solution | Tailwind CSS 4 | Accepted |

## 9.2 Decision Summary

### Technology Stack Decisions

The technology stack was chosen to balance developer productivity, performance, and alignment with the project's educational and quality assurance goals:

| Layer | Technology | Rationale |
|---|---|---|
| **Backend Framework** | FastAPI (Python 3.14) | Async-native, automatic OpenAPI docs, Pydantic validation, high performance |
| **Authentication** | fastapi-users + JWT | Production-ready user management, secure defaults, extensible |
| **Frontend Framework** | SvelteKit (Svelte 5) | Compile-time optimizations, minimal bundle size, no virtual DOM |
| **Styling** | Tailwind CSS 4 | Utility-first, consistent design system, automatic purging |
| **Database** | PostgreSQL 18 | ACID compliant, concurrent access, industry standard |
| **Maps** | OpenStreetMap / Leaflet | Free, no API key, global coverage, privacy-respecting |
| **Code Quality** | SonarCloud | Comprehensive static analysis, GitHub integration, quality gates |

### Architectural Decisions

| Decision | Description |
|---|---|
| **Layered Architecture** | Backend follows a three-layer pattern: Router → Service → Repository. Each layer has a single responsibility and is independently testable. |
| **Interface Abstraction** | Gas station data provider and data export are abstracted behind interfaces (ABCs), enabling easy swapping of implementations. |
| **Database Cache** | Tankerkönig API responses are cached in PostgreSQL with spatial and temporal metadata, reducing external API calls. |
| **Graceful Degradation** | When the Tankerkönig API is unavailable, the system returns an empty result list rather than failing. |
| **Rate Limiting** | Two-level rate limiting: per-user (SlowAPI) for the nearby stations endpoint, and global token-bucket for Tankerkönig API calls. |
| **Invitation-Only Registration** | User registration requires a valid invitation key, preventing unrestricted public signup. |
| **Dual DB Support** | The backend supports both PostgreSQL (production) and SQLite (development/testing) via a common async SQLAlchemy interface. |
| **Docker Compose Deployment** | All services (backend, frontend, database, monitoring) run in Docker containers, ensuring consistent environments. |

## 9.3 Not Yet Decided

The following architectural decisions remain open and may be addressed in future ADRs:

- **Reverse proxy selection:** Currently Nginx is used in production but no ADR has been written.
- **Database migration tool:** Currently `create_all` is used; Alembic may be considered for production schema migrations.
- **Caching backend for rate limits:** Currently in-memory; Redis may be considered for multi-process deployments.
- **CI/CD runner strategy:** Self-hosted vs GitHub-hosted runners for deployment.