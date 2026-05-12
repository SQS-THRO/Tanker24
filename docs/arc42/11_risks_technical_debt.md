# 11. Risks and Technical Debt

This page lists all identified risks and technical debts, ordered by priority. For each item, a mitigation or resolution strategy is proposed.

## 11.1 Risks

### R1: Tankerkönig API Unavailability (HIGH)

**Description:** The Tankerkönig API is provided on a best-effort basis with no uptime SLA. If the API becomes unavailable, Tanker24 loses its primary data source for gas prices, impacting use cases UC1 and UC2.

**Impact:** Users cannot search for current gas prices. The application's core value proposition is lost.

**Mitigation:**
- Implement graceful degradation: return an empty station list when the API is unreachable (already implemented).
- Cache station location data in the database to serve location information even without price data.
- Design the `GasStationService` as an abstract interface (implemented), enabling a future switch to an alternative data provider.

**Monitoring:** Uptime Kuma monitors backend health; Tankerkönig API errors are logged with coordinates for debugging.

---

### R2: Tankerkönig API Terms of Service Violation (MEDIUM)

**Description:** Tankerkönig's terms prohibit automated calls at exact hour changes and require that API calls are only made on user request. Misconfiguration of the rate limiter or caching could lead to violations.

**Impact:** Potential API key revocation or legal issues.

**Mitigation:**
- Global token-bucket rate limiter caps calls at 100/minute (configurable).
- Station cache with 30-minute expiry reduces API call frequency.
- Cache is checked before any API call; external calls only on cache miss.

---

### R3: Single Point of Failure — Deployment Server (MEDIUM)

**Description:** The entire application (frontend, backend, database) runs on a single virtual machine (`tanker24.eu`). Hardware failure or hosting provider outage would bring down the entire service.

**Impact:** Complete service unavailability until the server is restored.

**Mitigation:**
- Automated deployment via GitHub Actions reduces recovery time.
- Docker Compose configuration is version-controlled and portable.
- PostgreSQL data is stored on a persistent Docker volume.

**Future mitigation:** Consider deploying to a cloud platform with auto-scaling and multi-AZ database support.

---

### R4: No Database Backup Strategy (MEDIUM)

**Description:** There is no automated backup configured for the PostgreSQL database. A disk failure or accidental data deletion could result in permanent data loss.

**Impact:** Loss of user accounts, car data, and fueling history records.

**Mitigation:**
- Implement a scheduled `pg_dump` cron job on the production server.
- Store backups on an external storage service (e.g., S3-compatible storage).
- Document the disaster recovery procedure.

---

### R5: SQL Injection via Query Parameters (LOW)

**Description:** While SQLAlchemy ORM provides parameterized queries by default, direct string formatting in query building could introduce vulnerabilities.

**Impact:** Potential data exposure or corruption.

**Mitigation:**
- All database operations use SQLAlchemy ORM with parameterized queries.
- No raw SQL is executed in the application code.
- Code reviews verify adherence to this practice.

---

### R6: JWT Secret Exposure (LOW)

**Description:** If the `SECRET` environment variable (used for JWT signing) is leaked, an attacker could forge valid JWTs and impersonate any user.

**Impact:** Unauthorized access to all protected endpoints.

**Mitigation:**
- `SECRET` is stored in `.env` (not committed to git, in `.gitignore`).
- Production secrets are managed via environment variables set during deployment.
- `.env.example` contains a placeholder, not the actual secret.

---

## 11.2 Technical Debt

### TD1: No Database Migration Tool

**Description:** Table creation uses SQLAlchemy's `Base.metadata.create_all()` which is non-destructive but also non-migration-aware. Schema changes in production require manual intervention.

**Severity:** MEDIUM

**Resolution:** Adopt Alembic for schema migration management. Generate initial migration from current schema, then run `alembic upgrade head` during application startup.

---

### TD2: In-Memory Rate Limiting

**Description:** SlowAPI rate limits are stored in memory (`memory://` backend). In a multi-process or multi-container deployment, rate limits would not be shared.

**Severity:** LOW (single-process deployment suffices for current scale)

**Resolution:** If horizontal scaling is needed, switch to Redis-backed rate limiting using SlowAPI's Redis support or a dedicated Redis container.

---

### TD3: Frontend Test Coverage

**Description:** While the frontend has unit tests for services and stores, E2E tests are limited to the map page and login. Several routes lack E2E coverage.

**Severity:** MEDIUM

**Resolution:** Expand Playwright E2E test coverage to include registration, account management, and data export workflows.

---

### TD4: Missing Input Validation on Frontend

**Description:** Some form inputs on the frontend rely primarily on backend validation (Pydantic). Client-side validation could provide faster feedback.

**Severity:** LOW

**Resolution:** Add client-side validation for registration forms (password strength indicator, email format check) and station search (coordinate range checks).

---

### TD5: ER Model Documentation Outdated

**Description:** The ER model diagram in `docs/er-model.md` does not reflect the full database schema including `TankerkoenigStation`, `Station`, and `InvitationKey` tables.

**Severity:** LOW

**Resolution:** Update the ER diagram to include all tables present in the ORM models (`app/models.py`).

---

### TD6: Hardcoded Configuration in Containerfile

**Description:** The backend `Containerfile` embeds the build argument `SECRET` as an environment variable during image build, which embeds the secret in the container image layer.

**Severity:** MEDIUM

**Resolution:** Remove the `ARG SECRET` / `ENV SECRET` from the Containerfile. Secrets should only be injected at runtime via Docker Compose's `env_file` or Docker secrets.

---

### TD7: Test Concept Documentation Incomplete

**Description:** The `testConcept.md` documentation contains TODO markers for the GitHub pipeline test execution section, unit tests, integration tests, and smoke tests sections.

**Severity:** LOW

**Resolution:** Complete all remaining sections of the test concept documentation.

---

## 11.3 Risk and Debt Status Tracking

| ID | Category | Priority | Status |
|---|---|---|---|
| R1 | Tankerkönig API Unavailability | HIGH | Mitigated (graceful degradation + cache) |
| R2 | Terms of Service Violation | MEDIUM | Mitigated (rate limiter + cache) |
| R3 | Single Point of Failure | MEDIUM | Acknowledged |
| R4 | No Database Backup | MEDIUM | Open |
| R5 | SQL Injection | LOW | Mitigated (ORM usage) |
| R6 | JWT Secret Exposure | LOW | Mitigated (.env + .gitignore) |
| TD1 | No DB Migration Tool | MEDIUM | Open |
| TD2 | In-Memory Rate Limiting | LOW | Accepted for current scale |
| TD3 | Frontend Test Coverage | MEDIUM | Open |
| TD4 | Missing Frontend Validation | LOW | Open |
| TD5 | ER Model Outdated | LOW | Open |
| TD6 | Secret in Containerfile | MEDIUM | Open |
| TD7 | Test Concept Incomplete | LOW | Avoided by improving the test concept |