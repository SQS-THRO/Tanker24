# 6. Runtime View

This chapter describes the runtime behavior of Tanker24 by documenting the most important usage scenarios as sequence diagrams. Each scenario illustrates the interaction between the user, frontend, backend, database, and external systems.

## 6.1 Scenario: Search Nearby Gas Stations (UC1, UC7)

The user opens the map page, selects a location, and the system returns nearby gas stations with current prices.

```puml
@startuml
actor User
participant "Frontend\n(SvelteKit + Leaflet)" as FE
participant "Backend\n(FastAPI)" as BE
database "PostgreSQL" as DB
participant "Tankerkönig API" as TK

User -> FE: Opens the map page (/map)
FE -> FE: Gets user's current position\n(Geolocation API or map click)
FE -> BE: GET /api/v0/stations/nearby?latitude=X&longitude=Y\n(Authorization: Bearer <JWT>)

BE -> BE: Validates JWT token via fastapi-users
BE -> BE: Checks rate limit (10/min per user)
note right: SlowAPI/memory rate limiter

BE -> DB: SELECT * FROM tankerkoenig_stations\nWHERE cache_lat ≈ X AND cache_lon ≈ Y\nAND cache_radius = radius\nAND cached_at > now - 30 min
DB --> BE: Cached stations (or empty)

alt Cache hit (fresh data)
    BE -> BE: Data is recent enough
else Cache miss (stale or no data)
    BE -> BE: Acquires token from global rate limiter\n(100 req/min to Tankerkönig)
    BE -> TK: GET list.php?lat=X&lng=Y&rad=5&type=all&apikey=KEY
    TK --> BE: JSON: { "ok": true, "stations": [...] }
    BE -> DB: UPSERT stations with cache metadata\n(lat, lon, radius, cached_at timestamp)
    BE -> DB: DELETE stale stations not in new result set
end

BE --> FE: JSON: [{tankerkoenig_id, name, brand, diesel, e5, e10, distance, ...}]
FE -> FE: Renders markers on Leaflet map\nwith fuel prices in popups
FE --> User: Map is displayed with station markers
@enduml
```

**Steps:**
1. User navigates to `/map`; the SvelteKit frontend loads the Leaflet map component.  
2. The user selects a location (via geolocation or map click).  
3. Frontend sends `GET /api/v0/stations/nearby?latitude=X&longitude=Y` with the JWT token in the `Authorization` header.  
4. Backend validates the JWT and checks the user-based rate limit (10 requests per minute).  
5. Backend queries the `tankerkoenig_stations` cache table for matching entries within the configured tolerance (0.01 km) and expiry (30 minutes).  
6. **If cache hit:** cached stations are returned directly.  
7. **If cache miss:** the backend acquires a token from the global Tankerkönig rate limiter (100 requests/minute), then calls the Tankerkönig `list.php` API. Results are upserted into the cache with metadata (search coordinates, radius, timestamp). Stale entries from previous searches are cleaned up.  
8. Backend returns the station list as JSON with fuel prices and distances.  
9. Frontend renders station markers on the Leaflet map with price information.  

**Error Handling:**
- If the Tankerkönig API is unavailable, the service catches the exception, logs it, and returns an empty list (graceful degradation).
- If the user exceeds the rate limit, a `429 Too Many Requests` response is returned.
- If `latitude` or `longitude` are out of valid range, a `400 Bad Request` is returned.

## 6.2 Scenario: User Registration (UC5, UC6)

A new user registers with an invitation key.

```puml
@startuml
actor User
participant "Frontend\n(SvelteKit)" as FE
participant "Backend\n(FastAPI)" as BE
database "PostgreSQL" as DB

User -> FE: Navigates to /register\nfills form (email, password, forename, surname, invitation key)
FE -> FE: Client-side validation\n(password rules, required fields)
FE -> BE: POST /api/v0/auth/register\n{email, password, forename, surname, invitation_key}

BE -> BE: Validates password policy:\n- Min 8 chars\n- Upper + lower + digit + special char
BE -> BE: Checks if email already exists\n(UserAlreadyExists → 400)

BE -> DB: SELECT * FROM invitation_keys WHERE key = <key>
DB --> BE: InvitationKey (or None)

alt Invalid or missing invitation key
    BE --> FE: 400 Invalid invitation key
else Valid key
    BE -> BE: Hashes password with passlib
    BE -> DB: INSERT INTO users (... invitation_key_id=...)
    BE -> BE: Logs "User registered: id=X email=Y"
    BE --> FE: 201 Created {id, email, forename, surname, is_active, ...}
end

FE -> FE: Stores success message, redirects to /login
FE --> User: "Registration successful. Please log in."
@enduml
```

## 6.3 Scenario: Record Fuel Filling (UC3)

An authenticated user records a fuel filling event for one of their cars.

```puml
@startuml
actor User
participant "Frontend\n(SvelteKit)" as FE
participant "Backend\n(FastAPI)" as BE
database "PostgreSQL" as DB

User -> FE: Opens account page, selects a car,\nfills form (litres, price/litre, mileage, fuel type)
FE -> BE: POST /api/v0/cars/{car_id}/history\n{mileage, price_per_litre, litres, fuel_type_id}\n(Authorization: Bearer <JWT>)

BE -> BE: Validates JWT, extracts user ID
BE -> DB: SELECT * FROM cars WHERE id = car_id AND owner_id = user_id
DB --> BE: Car record (or 404)

BE -> DB: SELECT * FROM fuel_types WHERE id = fuel_type_id
DB --> BE: FuelType (diesel/e5/e10)

BE -> DB: INSERT INTO history_records\n(timestamp, mileage, price_per_litre, litres, car_id, fuel_type_id)
BE --> FE: 201 Created {id, timestamp, mileage, price_per_litre, litres, car_id, fuel_type_id}

FE -> FE: Updates history list on account page
FE --> User: "Filling recorded. Total: €XX.XX"
@enduml
```

## 6.4 Scenario: Export User Data (UC4)

The authenticated user exports their fueling history as JSON or CSV.

```puml
@startuml
actor User
participant "Frontend\n(SvelteKit)" as FE
participant "Backend\n(FastAPI)" as BE
database "PostgreSQL" as DB

User -> FE: Clicks "Export as JSON" or "Export as CSV"

alt JSON Export
    FE -> BE: GET /api/v0/export/json\n(Authorization: Bearer <JWT>)
    BE -> BE: Validates JWT, extracts user ID
    BE -> DB: SELECT cars WHERE owner_id = user_id
    DB --> BE: List of cars
    loop For each car
        BE -> DB: SELECT history_records WHERE car_id = X\nJOIN fuel_types
        DB --> BE: List of history records with fuel type names
    end
    BE -> BE: NestedExportDataService builds JSON:\n[{car, history: [{record, fuel_type}]}]
    BE --> FE: JSONResponse with Content-Disposition attachment

else CSV Export
    FE -> BE: GET /api/v0/export/csv\n(Authorization: Bearer <JWT>)
    BE -> BE: Validates JWT, extracts user ID
    BE -> DB: SELECT cars, history, fuel_types (same as JSON)
    DB --> BE: Data
    BE -> BE: FlatExportDataService flattens to CSV rows\nwith car_id repeated per row\n(using semicolon delimiter)
    BE --> FE: StreamingResponse (text/csv) with Content-Disposition attachment
end

FE -> FE: Triggers browser download
FE --> User: File is downloaded
@enduml
```

## 6.5 Scenario: Application Startup

```puml
@startuml
participant "Docker Compose" as DC
participant "Backend (FastAPI)" as BE
database "PostgreSQL" as DB

DC -> BE: docker compose up -d\n(startup)

BE -> BE: setup_logging()\nStructured logging to stdout\nSQLAlchemy: WARNING (INFO in debug)
BE -> BE: init_db()\nSQLAlchemy: Base.metadata.create_all\n(Creates tables if not existing)
BE -> DB: CREATE TABLE IF NOT EXISTS\n(users, cars, history_records,\nstations, tankerkoenig_stations,\ninvitation_keys, fuel_types)

BE -> BE: sync_invitation_keys()\nReads INVITATION_KEYS from env
BE -> DB: SELECT * FROM invitation_keys
DB --> BE: Existing DB keys
BE -> BE: Key diff: env vs DB
BE -> DB: DELETE keys not in env\n(unset invitation_key_id for affected users)
BE -> DB: INSERT new keys from env

BE -> BE: "Application startup complete"
BE --> DC: Ready to serve requests on port 8000
@enduml
```

**Startup Steps:**
1. Docker Compose starts the backend container (after PostgreSQL is healthy).  
2. `lifespan` context manager calls `setup_logging()` to configure structured logging.  
3. `init_db()` runs `Base.metadata.create_all` to create any missing tables (idempotent).  
4. `sync_invitation_keys()` reads the `INVITATION_KEYS` environment variable (comma-separated 32-char hex strings), diff against the DB, removes expired keys, and adds new ones. Users with deleted keys have their `invitation_key_id` set to `NULL`.  
5. The application starts serving requests on port 8000.  