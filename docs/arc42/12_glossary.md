# 12. Glossary

| Term | Definition |
|---|---|
| **ADRs** | Architecture Decision Records — structured documents describing important architectural decisions, their context, rationale, and consequences. |
| **aiosqlite** | Async SQLite driver for Python, used by SQLAlchemy for async SQLite operations in development and testing. |
| **Alembic** | A database migration tool for SQLAlchemy (not yet adopted, identified as technical debt TD1). |
| **asyncpg** | Async PostgreSQL driver for Python, providing high-performance async database access. |
| **ASGI** | Asynchronous Server Gateway Interface — the standard for Python async web servers. Uvicorn is the ASGI server used by Tanker24. |
| **CI/CD** | Continuous Integration / Continuous Delivery — the automated pipeline that builds, tests, and deploys the application on every code change. |
| **CORS** | Cross-Origin Resource Sharing — a browser security mechanism. The backend allows CORS from configured origins (`CORS_ORIGINS`). |
| **Docker Compose** | Tool for defining and running multi-container Docker applications. Tanker24's `compose.yaml` defines 4 services. |
| **E2E** | End-to-End testing — tests that simulate real user interactions in a browser using Playwright. |
| **E5, E10** | European fuel type designations: E5 (up to 5% ethanol), E10 (up to 10% ethanol). Both are common gasoline types in Germany. |
| **fastapi-users** | A Python library providing ready-to-use user authentication and management for FastAPI applications, including JWT, OAuth2, registration, and password recovery. |
| **FastAPI** | A modern, fast (high-performance) Python web framework for building REST APIs, based on Starlette and Pydantic. |
| **Fuel Type** | The category of fuel: Diesel, E5 (Super), or E10 (Super with ethanol). Stored in the `fuel_types` table. |
| **Gas Station** | A petrol/fuel station that sells Diesel, E5, and/or E10 fuel. Data is obtained from the Tankerkönig API and cached in the database. |
| **GitHub Container Registry (ghcr.io)** | GitHub's Docker container registry. Tanker24 pushes built container images to `ghcr.io/SQS-THRO/` for deployment. |
| **History Record** | A single fuel filling event recorded by a user, containing timestamp, mileage, price per litre, litres filled, and fuel type. |
| **Invitation Key** | A 128-bit hex string (32 characters) required for user registration. Configured by the administrator via the `INVITATION_KEYS` environment variable. Prevents open public registration. |
| **JWT (JSON Web Token)** | A compact, URL-safe token used for stateless authentication. Tanker24 uses JWT bearer tokens signed with the `SECRET` key. |
| **Leaflet** | An open-source JavaScript library for interactive maps. Used by the frontend to render map tiles and station markers. |
| **MkDocs** | A static site generator for project documentation. Tanker24 uses MkDocs with the Material theme and PlantUML plugin. |
| **MTS-K (Markttransparenzstelle für Kraftstoffe)** | The German Federal Cartel Office's Market Transparency Unit for Fuels. Provides the official API for German gas station prices. Tanker24 accesses this data indirectly through Tankerkönig. |
| **Mypy** | A static type checker for Python. Runs in CI to catch type errors before they reach production. |
| **Playwright** | An end-to-end testing framework by Microsoft. Used for browser-based testing of the frontend. |
| **PostgreSQL** | A powerful, open-source relational database system. Used as the production database for Tanker24. |
| **Pydantic** | A Python data validation library using type annotations. Used by FastAPI for request/response validation and by the backend for schema definitions. |
| **Rate Limiting** | A mechanism to control the frequency of requests. Tanker24 applies per-user rate limits (SlowAPI) for the nearby stations endpoint and a global rate limit (token bucket) for Tankerkönig API calls. |
| **ReadTheDocs** | A documentation hosting platform. Tanker24's documentation is hosted at [tanker24.readthedocs.io](https://tanker24.readthedocs.io). |
| **Ruff** | A fast Python linter and code formatter written in Rust. Replaces Flake8, isort, and Black in Tanker24's toolchain. |
| **SlowAPI** | A rate-limiting library for FastAPI/Starlette. Used to enforce per-user rate limits on API endpoints. |
| **SonarCloud** | A cloud-based code quality and security analysis service by SonarSource. Monitors code quality, coverage, bugs, and vulnerabilities for both backend and frontend. |
| **SQLAlchemy** | The Python SQL toolkit and Object-Relational Mapper (ORM). Used for all database operations with async support. |
| **Svelte / SvelteKit** | A modern frontend framework that compiles components to vanilla JavaScript at build time. SvelteKit provides routing, SSR, and deployment tooling. |
| **TailwindCSS** | A utility-first CSS framework for rapid UI development. Used for all frontend styling with automatic purging of unused styles in production. |
| **Tankerkönig** | A free, community-driven API service (`creativecommons.tankerkoenig.de`) that provides access to German gas station price data from the MTS-K. |
| **Token Bucket** | A rate-limiting algorithm where tokens accumulate at a fixed rate. Each API call consumes one token. Used by the global Tankerkönig rate limiter. |
| **Uptime Kuma** | A self-hosted monitoring tool for tracking service uptime. Monitors the health of frontend and backend services. |
| **Uvicorn** | An ASGI web server implementation for Python. Runs the FastAPI application in production. |
| **Vite** | A modern frontend build tool. Used by SvelteKit for development server, hot module replacement, and production builds. |
| **Vitest** | A Vite-native unit testing framework. Used for frontend unit tests (services, stores, utilities). |