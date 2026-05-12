# 10. Quality

## 10.1 Quality Tree

Building on the quality goals defined in [Section 1.2](01_intro_goals.md#12-quality-goals), the following quality tree structures the quality requirements into a hierarchy:

```
Quality
├── Functional Stability
│   ├── All main use cases implemented
│   └── Bug-free core functionality
├── Reliability
│   ├── Graceful recovery from Tankerkönig API outages
│   ├── Cache-based fallback for station data
│   └── Zero data loss on failure
├── Security
│   ├── Authenticated access to user data
│   ├── Strong password policy enforcement
│   ├── JWT token-based session management
│   └── Invitation-only registration
├── Transferability
│   ├── JSON export of user data
│   └── CSV (semicolon-separated) export
├── Maintainability
│   ├── Clean architecture (layered)
│   ├── Automated code quality checks
│   └── Comprehensive documentation (arc42 + ADRs)
├── Performance Efficiency
│   ├── Fast API response times
│   ├── Cached station data (reduced external calls)
│   └── Minimal frontend bundle size (Svelte compiler)
├── Operability
│   ├── Single-command deployment (docker compose up -d)
│   ├── Structured logging to stdout
│   └── Health check endpoint
└── Compatibility
    ├── Modern browser support (Chromium-based)
    ├── Responsive design (mobile + desktop)
    └── PostgreSQL + SQLite database backends
```

## 10.2 Quality Scenarios

Quality scenarios describe concrete, measurable quality requirements using the standard template: *Stimulus → System → Response → Metric*.

### 10.2.1 Functional Stability

| ID | Scenario | Stimulus | Response | Metric |
|---|---|---|---|---|
| QS-FS-01 | All main use cases (UC1–UC7) are implemented and operational | User requests any main use case | System fulfills the use case correctly | 100% of main use cases pass acceptance tests |
| QS-FS-02 | No regression in existing functionality | Developer pushes code changes | CI pipeline runs full test suite | All tests pass before merge |

### 10.2.2 Reliability

| ID | Scenario | Stimulus | Response | Metric |
|---|---|---|---|---|
| QS-REL-01 | Tankerkönig API returns HTTP 5xx error | A user searches for nearby stations during an API outage | System returns an empty list (graceful degradation) and logs the error | Application remains available (no 500 errors); degraded response within 2s |
| QS-REL-02 | Tankerkönig API is slow (>5s response) | A user searches for nearby stations | System times out at 10s, returns empty list, logs warning | Response time to user ≤ 10s |
| QS-REL-03 | PostgreSQL database connection is temporarily lost | A database query fails mid-request | SQLAlchemy/session error is caught, transaction rolled back, appropriate HTTP error returned | No data corruption; error returned within 5s |

### 10.2.3 Security

| ID | Scenario | Stimulus | Response | Metric |
|---|---|---|---|---|
| QS-SEC-01 | Unauthenticated user accesses protected endpoint | Request without valid JWT | System returns HTTP 401 Unauthorized | 100% of protected endpoints reject unauthenticated requests |
| QS-SEC-02 | User attempts registration without valid invitation key | Registration with invalid/empty key | System rejects with "Invalid invitation key" error | Unauthorized registrations blocked with 100% accuracy |
| QS-SEC-03 | User provides weak password | Registration with password failing policy | System rejects with specific password requirement message | All 5 policy rules enforced (len, upper, lower, digit, special) |
| QS-SEC-04 | JWT token expires | Request with expired JWT | System returns HTTP 401, requires re-login | Token expiry honored within 1 second of expiration |
| QS-SEC-05 | Brute force login attempt | Many rapid login requests | Rate limiting on auth endpoints prevents abuse | Rate limited per SlowAPI configuration |

### 10.2.4 Transferability

| ID | Scenario | Stimulus | Response | Metric |
|---|---|---|---|---|
| QS-TRF-01 | User requests JSON export | GET /api/v0/export/json | System returns nested JSON with all cars and history records | Complete user data exported; file downloads with correct Content-Disposition header |
| QS-TRF-02 | User requests CSV export | GET /api/v0/export/csv | System returns semicolon-separated CSV with flat rows | Complete user data exported as valid CSV; all columns present |

### 10.2.5 Maintainability

| ID | Scenario | Stimulus | Response | Metric |
|---|---|---|---|---|
| QS-MNT-01 | New developer needs to understand the architecture | Developer reads the documentation | arc42 documentation provides a complete architecture overview | All 12 arc42 sections are populated with project-specific content |
| QS-MNT-02 | Code linting violation | Developer pushes code with style issues | Ruff/ESLint reports violations in CI | Build fails on lint errors |
| QS-MNT-03 | Type error in backend code | Developer writes type-unsafe code | Mypy reports type violations in CI | Build fails on type errors |
| QS-MNT-04 | New external API provider needed | Need to replace Tankerkönig with another provider | Implement new GasStationService subclass, inject into NearbyStationsService | New provider implemented in <2 days without changes to consumers |

### 10.2.6 Performance Efficiency

| ID | Scenario | Stimulus | Response | Metric |
|---|---|---|---|---|
| QS-PERF-01 | User searches for nearby stations (cache hit) | GET /api/v0/stations/nearby | Cached stations returned from PostgreSQL | Response time ≤ 200ms (p95) |
| QS-PERF-02 | User searches for nearby stations (cache miss) | GET /api/v0/stations/nearby (no cache) | Tankerkönig API called, results cached, returned | Response time ≤ 5s |
| QS-PERF-03 | Frontend initial page load | User navigates to the application | SvelteKit renders page, maps load | First Contentful Paint ≤ 2s |
| QS-PERF-04 | Concurrent station searches | Multiple users search simultaneously | Rate limiter gates external API calls | Tankerkönig API calls ≤ 100/min regardless of user count |

### 10.2.7 Operability

| ID | Scenario | Stimulus | Response | Metric |
|---|---|---|---|---|
| QS-OPS-01 | System startup | `docker compose up -d` | All 4 services start, backend initializes DB schema | Full startup ≤ 30 seconds |
| QS-OPS-02 | Health monitoring | Uptime Kuma polls /health | 200 OK with status, name, and version | Health check always returns correct status |
| QS-OPS-03 | Application logs available | Administrator needs to debug an issue | Structured logs written to stdout | Log format: `timestamp \| LEVEL \| module \| message` |
| QS-OPS-04 | Zero-downtime redeployment | New version deployed via CI/CD | `docker compose pull && up -d` rolls containers | Downtime ≤ 5 seconds |

## 10.3 Code Quality Pipeline

### 10.3.1 Automated Quality Checks

Every code change must pass the following pipeline before merging:

```
┌─────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────────┐
│  Developer   │────▶│ Pre-commit│────▶│ CI Pipeline│────▶│ SonarCloud   │
│  writes code │     │ (local)  │     │ (GitHub)  │     │ Quality Gate │
└─────────────┘     └──────────┘     └──────────┘     └──────────────┘
```

| Stage | Checks | Tool |
|---|---|---|
| **Local** | Linting, formatting, type checking | Ruff, Prettier, ESLint, Mypy, Local SonarQube |
| **CI (Backend)** | Linting, formatting, type checking, unit/integration tests, coverage | Ruff, Mypy, pytest-cov |
| **CI (Frontend)** | Linting, formatting, unit tests, E2E tests | ESLint, Prettier, Vitest, Playwright |
| **Quality Gate** | Comprehensive analysis: bugs, vulnerabilities, smells, coverage, duplication | SonarCloud |

### 10.3.2 Code Coverage Target

The project targets **≥80% code coverage** for both backend and frontend codebases. Coverage reports are generated during CI runs and uploaded to SonarCloud for tracking.

### 10.3.3 Code Review Convention

As defined in [Section 2](02_constraints.md):
- Every pull request requires at least one code review before merging to `main`.
- Issues include a description, user story (optional), and measurable acceptance criteria.
- Pull requests include a short description and link to the related issue.