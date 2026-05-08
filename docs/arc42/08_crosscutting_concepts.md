# 8. Crosscutting Concepts

## 8.1 Domain Model

The domain model reflects the core entities of the application:

- **User**: Authenticated driver who owns cars and tracks fueling history.
- **Car**: A vehicle associated with a user, identified by license plate.
- **FuelType**: Enumeration of fuel types (Diesel, E5, E10).
- **HistoryRecord**: A single fueling event with timestamp, mileage, price, liters, and fuel type.
- **TankerkoenigStation**: Cached gas station data from the external Tankerkönig API with spatial metadata.

The complete data model is documented in the [Entity-Relationship Model](../er-model.md) and in [Section 5.2.4](05_building_block_view.md#524-data-model-orm).

## 8.2 Authentication and Authorization

Tanker24 uses the **fastapi-users** library with JWT-based bearer token authentication.

### 8.2.1 Authentication Flow

1. **Registration** (`POST /api/v0/auth/register`): User provides email, password, forename, surname, and an invitation key. The password is validated against a policy (min 8 chars, uppercase, lowercase, digit, special character). The invitation key is checked against the `invitation_keys` database table.
2. **Login** (`POST /api/v0/auth/jwt/login`): User provides email and password via form-encoded body. The server validates credentials and returns a JWT access token (`access_token` + `token_type: "bearer"`).
3. **Token Usage**: All protected endpoints require the JWT in the `Authorization: Bearer <token>` header. The `get_current_active_user` FastAPI dependency validates the token and returns the user object.
4. **Token Expiry**: JWTs expire after the configured lifetime (default: 60 minutes, configurable via `JWT_LIFETIME_MINUTES`).

### 8.2.2 Authorization Levels

| Level | Access |
|---|---|
| **Unauthenticated** | Health check (`/health`, `/`), Login, Register |
| **Authenticated (active)** | CRUD stations, nearby search, data export, user profile |
| **Superuser** | User management (via fastapi-users built-in routes) |

### 8.2.3 Invitation Key System

- Invitation keys are 128-bit hex strings (32 characters) configured in the `INVITATION_KEYS` environment variable.
- On application startup, keys are synced: new keys from env are added to the DB; keys removed from env are deleted (users retain their accounts but lose the key association).
- Registration requires a valid invitation key to prevent open public registration.

## 8.3 Persistence

### 8.3.1 Dual Database Support

Tanker24 supports two database backends, configured via the `DB_TYPE` environment variable:

| Backend | Driver | Use Case |
|---|---|---|
| **PostgreSQL** | `asyncpg` | Production deployment with concurrent access, data integrity, and scalability |
| **SQLite** | `aiosqlite` | Local development and testing (including in-memory `:memory:` mode) |

The `database_url` property in `Settings` builds the connection string dynamically based on the configured DB type.

### 8.3.2 Async ORM

SQLAlchemy 2.0 is used with the async extension (`sqlalchemy.ext.asyncio`). All database operations use `AsyncSession` obtained via FastAPI dependency injection (`get_db`). The session factory (`async_session_maker`) is configured with `expire_on_commit=False` to avoid detached instance issues.

### 8.3.3 Schema Management

Table creation is handled at application startup via `Base.metadata.create_all()` — an idempotent operation suitable for this project's scope. No migration framework (e.g., Alembic) is used at this stage.

## 8.4 Caching Strategy

### 8.4.1 Gas Station Data Cache

To minimize calls to the external Tankerkönig API, station data is cached in the `tankerkoenig_stations` database table:

| Cache Parameter | Value | Config Key |
|---|---|---|
| Expiry time | 30 minutes | `STATION_CACHE_EXPIRY_MINUTES` |
| Spatial tolerance | 0.01 km | `STATION_CACHE_TOLERANCE_KM` |
| Search radius | 5.0 km | `TANKERKOENIG_SEARCH_RADIUS_KM` |

**Cache lookup logic:**
- Query stations where `cache_lat` and `cache_lon` are within tolerance of the request coordinates, `cache_radius` matches, and `cached_at` is within the expiry window.
- On cache hit, return cached stations directly.
- On cache miss, fetch from Tankerkönig API, upsert into cache, and clean up stale entries.

**Cache update strategy:** Stale entries (stations that were in the previous cache set but are not in the new API response) are deleted during upsert to prevent accumulation of outdated data.

## 8.5 Rate Limiting

Tanker24 implements rate limiting at two levels:

### 8.5.1 User-Level Rate Limiting (SlowAPI)

The `/stations/nearby` endpoint is rate-limited per authenticated user:

```python
@limiter.limit(settings.nearby_stations_rate_limit)  # default: 10/minute
```

The rate limit key function (`get_rate_limit_key`) uses the authenticated user ID when available, falling back to IP address for unauthenticated requests. Rate limits are stored in memory using SlowAPI's `memory://` storage backend.

### 8.5.2 API-Level Rate Limiting (Token Bucket)

A custom token-bucket rate limiter (`RateLimiter` class in `app/services/rate_limiter.py`) controls the frequency of calls to the Tankerkönig external API:

- **Limit:** 100 requests per 60 seconds (configurable via `TANKERKOENIG_RATE_LIMIT_PER_MINUTE`)
- **Algorithm:** Token bucket with smooth refill, using `asyncio.Lock` for thread safety in async context
- **Behavior:** Before each API call, `await global_rate_limiter.wait_for_token()` blocks until a token is available

This prevents exceeding Tankerkönig's terms of service limits and avoids hammering the external API during high traffic.

## 8.6 Logging

### 8.6.1 Structured Logging

Logging is configured at application startup via `setup_logging()`:

- **Format:** `YYYY-MM-DD HH:MM:SS | LEVEL | module | message`
- **Output:** `stdout` (console-friendly, Docker-compatible)
- **Level:** Configurable via `LOG_LEVEL` env variable (default: `INFO`)

### 8.6.2 Log Levels by Component

| Component | Default Level | Debug Level |
|---|---|---|
| Application (`app.*`) | `LOG_LEVEL` (env) | DEBUG |
| Uvicorn access | `WARNING` | INFO |
| SQLAlchemy engine | `WARNING` | INFO (when `DEBUG=true`) |

### 8.6.3 Request Logging Middleware

A custom `RequestLoggingMiddleware` logs each incoming request with method, path, status code, and duration in milliseconds:

```
2026-05-08 12:34:56 | INFO     | app.main | GET /api/v0/stations/nearby -> 200 (234.5ms)
```

## 8.7 Error Handling

### 8.7.1 Backend Error Strategy

| Error Type | HTTP Status | Handling |
|---|---|---|
| Validation error (Pydantic) | 422 | FastAPI/Pydantic auto-generates detail messages |
| Authentication failure | 401 | Returned by fastapi-users JWT validation |
| Authorization failure (ownership) | 404 | Station not owned by user returned as "not found" |
| Rate limit exceeded | 429 | Custom handler for `RateLimitExceeded` exception |
| Tankerkönig API failure | 200 (empty list) | Exception logged, empty list returned (graceful degradation) |
| Database error (export) | 503 | Transaction rolled back, generic error returned |

### 8.7.2 Graceful Degradation

When the Tankerkönig API is unavailable (network error, timeout, bad response), the `NearbyStationsService` catches the exception, logs it, and returns an empty station list rather than propagating a 500 error to the user. This ensures the application remains functional even if the external data source is down.

## 8.8 Internationalization (i18n)

The frontend supports multiple languages using `svelte-i18n`:

- **Supported languages:** English (default), German
- **Language switcher:** `LanguageSwitcher` component in the navbar toggles the active locale
- **Store:** `$lib/stores/locale.ts` manages the current locale state
- **Persistence:** The user's language preference is stored and applied on subsequent visits

## 8.9 Theming

The frontend supports light and dark themes:

- **Theme detection:** Follows system preference (`prefers-color-scheme`)
- **Theme store:** `$lib/stores/theme.ts` manages theme state
- **Map theming:** Switches between OpenStreetMap Standard tiles (light) and CartoDB Dark Matter tiles (dark) based on the active theme
- **UI styling:** TailwindCSS 4's dark mode utilities with `class` strategy

## 8.10 Testing Strategy

Tanker24 follows the test automation pyramid:

### 8.10.1 Backend Tests (pytest)

| Test Type | Tool | Scope |
|---|---|---|
| **Unit tests** | pytest, pytest-asyncio | Individual functions, services, models |
| **Integration tests** | pytest + SQLite test DB | Database repositories, API endpoints via TestClient |
| **Architecture tests** | pytest | Enforces architectural rules (layer dependencies, imports) |
| **Code coverage** | pytest-cov | Target: ≥80% |

Backend tests use SQLite as the test database (faster, no external dependencies) and are configured in `pytest.ini` with `asyncio_mode = auto`.

### 8.10.2 Frontend Tests (Vitest + Playwright)

| Test Type | Tool | Scope |
|---|---|---|
| **Unit tests** | Vitest | Services (`*.test.ts`), stores (`*.test.ts`), utility functions |
| **E2E tests** | Playwright (Chromium) | Full browser-based user journeys: map page, login flow |

Playwright tests (`*.e2e.ts`) run against the production build, simulating real user interactions.

### 8.10.3 CI Integration

All tests are executed in GitHub Actions CI:
- `test_backend.yml`: pytest with coverage → `coverage.xml`
- `test_frontend.yml`: vitest + Playwright
- `sonarcloud.yml`: Aggregates both coverage reports for SonarCloud analysis

## 8.11 Code Quality

### 8.11.1 Static Analysis

| Tool | Language | Checks |
|---|---|---|
| **Ruff** | Python | Linting, import sorting, code formatting |
| **Mypy** | Python | Static type checking (strict mode) |
| **ESLint** | TypeScript/JS | Code quality rules |
| **Prettier** | TypeScript/JS/CSS | Code formatting |
| **SonarCloud** | All | Comprehensive code quality analysis (bugs, smells, vulnerabilities, coverage, duplication) |

### 8.11.2 Quality Gate

SonarCloud is configured via `sonar-project.properties` and enforces:
- No new bugs or vulnerabilities
- Code coverage threshold
- Maintainability rating
- No duplicated code blocks

Results are displayed as badges in the README and block PR merges when the quality gate fails.

## 8.12 Interface Abstraction

### 8.12.1 Gas Station Data Provider

The `GasStationService` abstract base class defines the interface for gas station data providers:

```python
class GasStationService(ABC):
    def get_gas_station_by_id(self, id: str) -> GasStation: ...
    def get_gas_stations(self, latitude, longitude, radius) -> List[GasStation]: ...
```

The current implementation, `TankerkoenigGasStationService`, communicates with the Tankerkönig REST API. This abstraction allows swapping to a different data provider (e.g., a self-hosted database replica) without changing the consuming services.

### 8.12.2 Data Export

The `ExportDataService` abstract base class defines the interface for data export:

```python
class ExportDataService(ABC):
    async def get_user_data(self, user_id: int) -> list[dict[str, Any]]: ...
```

Two implementations exist:
- `NestedExportDataService`: Returns hierarchical JSON (cars → history records)
- `FlatExportDataService`: Returns flat CSV-compatible rows (one row per history record with car details repeated)

## 8.13 Privacy and Consent

The frontend implements a consent management system:
- **ConsentModal**: Displays privacy policy and requests user consent on first visit
- **Privacy store** (`$lib/stores/privacy.ts`): Manages consent state
- **GDPR compliance**: Privacy policy available at `/privacy`, legal imprint at `/impressum`
- **No tracking**: No third-party analytics or tracking cookies are used