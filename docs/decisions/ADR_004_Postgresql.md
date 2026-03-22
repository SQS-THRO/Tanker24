# ADR 004: Choosing PostgreSQL DB as database

**Date:** 2026-03-19  
**Context:** Data Persistance and Caching

---

## 1. Context

Our project requires a modern, performant, and well supported relational databse. The key requirements include:

- High performance and low latency
- Native support in Python
- Easy setup with a Dockerfile or in docker compose
- Robust and well-proven

We evaluated several Python databases to determine the best fit for our requirements.

---

## 2. Decision

We decided to adopt **PostgreSQL** as the primary database for our application.

---

## 3. Rationale

### Benefits of using PostgreSQL:

- **Concurrency & Scalability**:
	- Allows for true parallel reads/writes
	- Handles multiple read at the same time with ease
	- Database can be easily moved to a different server for hardware boost
- **Better Production Experience**
	- server-based database proven in industry for heavy duty production settings
	- good community support
	- high configurability
	- ensures data integrity under heavy loads
- **Data Integrity & Reliability**
	- ACID compliance given at all times
	- Transaction isolation for concurrent requests
	- Good constraint setup in tables

### Alternatives considered:

| Option | Pros | Cons |
|--------|------|------|
| SQLite | Lightweight, easy setup | Very limited concurrency and performance under load. Not scaleable. |
| MariaDB | Simplicity, MySQL-compatible ecosystem, fast | less strong sql dialect, data integrity strongly depends on proper configuration, no longer industry standard |


PostgreSQL is the current industry standard for relational server-based databases.

---

## 4. Consequences

### Positive Outcomes

- Easy integration of the database into the application
- Highly scaleable architecture
- Modern best choices applied

### Tradeoffs and Considerations

- Slightly more complicated setup and maintenance of the database

---

## 5. References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MariaDB Documentation](https://mariadb.com/docs)
- [SQLLite Documentation](https://sqlite.org/docs.html)