---
icon: simple/fastapi
---

# ADR 002: Choosing `fastapi-users` for User Authentication

**Date:** 2026-03-18  
**Context:** Security, Developer Productivity, Scalability  

---

## 1. Context

In our project, we require robust user authentication and authorization features, including:

- User registration and login
- Password hashing and validation
- JWT-based authentication
- OAuth2 support (Google, GitHub, etc.)
- Email verification and password recovery
- Role-based access control (RBAC)
- Integration with a FastAPI-based backend

Instead of implementing all of these features manually, we evaluated third-party libraries to ensure maintainability, security, and reduced time-to-market. One key candidate was [`fastapi-users`](https://github.com/fastapi-users/fastapi-users).

---

## 2. Decision

We decided to adopt the [`fastapi-users`](https://github.com/fastapi-users/fastapi-users) library for handling user authentication and authorization in our application.

---

## 3. Rationale

### Benefits of using `fastapi-users`:

- **Out-of-the-box features**:
	- Complete user management: registration, login, reset password, verify email, etc.
	- JWT and OAuth2 support
	- Ready-to-use routers and dependencies
- **Security Best Practices**:
	- Follows FastAPI and OAuth2 best practices
	- Secure password hashing with `passlib`
	- Automatic token revocation mechanisms via blacklist or token rotation strategies
- **Modularity**:
	- Easily extensible user model
	- Customizable database backends (SQLAlchemy, MongoDB, etc.)
- **Community Support & Maintenance**:
	- Active open-source community
	- Compatible with FastAPI's evolution and ecosystem
- **Developer Productivity**:
	- Minimizes boilerplate and duplicated logic
	- Reduces onboarding time for new developers

### Alternatives considered:

| Option | Pros | Cons |
|-------|------|------|
| Manual Implementation | Full control; tailored logic | High dev time, security risks, increased maintenance |
| Auth0 / Firebase Auth | Hosted; scalable | Vendor lock-in, less control, integration complexity |
| Django Rest Auth | Mature, feature-rich | Heavyweight, not aligned with FastAPI's async stack |
| FastAPI JWT Auth | Lightweight and flexible | Less batteries-included; missing user workflows |

`fastapi-users` struck the right balance between flexibility, feature-completeness, and alignment with FastAPI's async-first design.

---

## 4. Consequences

### Positive Outcomes

- Faster implementation of secure user auth workflows
- Consistent and tested foundation for auth features
- Easier onboarding for team members familiar with FastAPI
- Lower long-term maintenance cost

### Tradeoffs and Considerations

- Tied to the evolution and maintenance of `fastapi-users`
- Requires understanding of its abstraction layers (UserDB, routers, mixins)
- Some advanced customization may require deeper integration effort

---

## 5. References

- [`fastapi-users` Documentation](https://fastapi-users.github.io/fastapi-users/)
- [FastAPI Authentication Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)


