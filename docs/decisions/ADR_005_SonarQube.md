---
icon: simple/sonar
---

# ADR 005: Choosing SonarQube for Code Quality Analysis

**Date:** 2026-03-24  
**Context:** Code Quality, Security, Developer Productivity  

---

## 1. Context

Our project requires a comprehensive code quality and static analysis solution to maintain high standards of code health. The key requirements include:

- Static analysis for code smells, bugs, and vulnerabilities
- Security vulnerability detection
- Code coverage integration
- Language support for Python (backend) and Svelte/TypeScript (frontend)
- CI/CD pipeline integration
- Self-hosted option for data privacy and control

We evaluated several code quality platforms to determine the best fit for our requirements.

---

## 2. Decision

We decided to adopt **SonarQube** as the primary code quality analysis platform for our application.

---

## 3. Rationale

### Benefits of using SonarQube:

- **Comprehensive Analysis**:
	- Detects bugs, code smells, security vulnerabilities, and security hotspots
	- Supports multiple languages including Python, TypeScript, JavaScript, and more
	- Tracks code coverage and duplication
- **Self-Hosted Deployment**:
	- Can be run locally via Docker for full data control
	- No dependency on external services or subscription costs
	- Configurable to meet project-specific needs
- **CI/CD Integration**:
	- Seamless integration with GitHub Actions, GitLab CI, and other CI tools
	- Quality Gates to block merges on failing criteria
	- Pull request decoration for inline feedback
- **Community Edition Available**:
	- Free self-hosted option with robust features
	- No vendor lock-in or usage-based pricing
- **Industry Standard**:
	- Widely adopted in enterprise and open-source projects
	- Strong documentation and community support

### Alternatives considered:

| Option | Pros | Cons |
|--------|------|------|
| Embold | Free tier, multi-language support, SaaS option | Official service experiencing intermittent HTTP 502 Gateway errors; unreliable availability |
| Code Climate | GitHub-integrated, well-designed UI, test coverage tracking | Limited free tier, pricing based on lines of code, no self-hosted option |
| Codacy | Easy setup, GitHub integration, supports many languages | Free tier limited, no self-hosted option, pricing scales with repo size |

**Embold** was rejected due to unreliable service availability with the official platform experiencing intermittent HTTP 502 Gateway errors, making it unsuitable for consistent code quality monitoring.

**Code Climate** and **Codacy** were not chosen due to limited free tiers, pricing models based on codebase size, and lack of self-hosted deployment options.

SonarQube provides the best balance of features, self-hosting capability, and reliability.

---

## 4. Consequences

### Positive Outcomes

- Comprehensive code quality insights across all supported languages
- Full control over data and infrastructure with self-hosted deployment
- Integration with existing CI/CD pipeline for automated quality gates
- Improved security posture through vulnerability detection
- No ongoing subscription costs with Community Edition

### Tradeoffs and Considerations

- Requires maintenance and updates for self-hosted instance
- Initial configuration may require tuning for project-specific rules
- More resource-intensive than lightweight linters alone
- Some advanced features require paid editions (SonarQube Developer/Enterprise)

---

## 5. References

- [SonarQube Documentation](https://docs.sonarqube.org/)
- [SonarQube GitHub](https://github.com/SonarSource/sonarqube)
- [SonarCloud](https://sonarcloud.io/) (cloud-hosted alternative)
