<!--
Sync Impact Report
Version change: 1.0.0 → 1.1.0
Modified principles: All replaced with enterprise-grade principles
Added sections: Technology & Compliance, Development Workflow
Removed sections: None
Templates requiring updates: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md
Follow-up TODOs: TODO(RATIFICATION_DATE): Original adoption date required
-->

# SpendPlatform Constitution

## Core Principles

### I. Secure Architecture

All code MUST follow OWASP, PTES, and NIST SP 800-115 methodologies. Security is non-negotiable: input validation, output encoding, least privilege, encrypted secrets, secure password storage, and regular vulnerability scans are mandatory. Authentication uses JWT/OAuth2, biometric integration, and optional MFA. Rationale: Enterprise-grade security is foundational for user trust and compliance.

### II. Separation of Concerns

The codebase MUST maintain strict separation between backend (FastAPI), frontend (React), database (PostgreSQL), reporting (Superset/Metabase), and deployment (Docker). Directory structure MUST reflect this separation. Rationale: Clean separation enables maintainability, scalability, and auditability.

### III. Test-Driven Development (NON-NEGOTIABLE)

TDD is mandatory: all features require failing tests before implementation. Automated unit, integration, and security tests MUST be written and maintained. Rationale: TDD ensures reliability, security, and rapid regression detection.

### IV. Integration & Observability

Integration tests are required for all inter-service communication, shared schemas, and contract changes. Structured logging, monitoring, and alerting MUST be implemented. Reporting endpoints MUST be secured. Rationale: Observability and integration testing are critical for enterprise reliability and compliance.

### V. Versioning & Simplicity

Versioning follows semantic rules: MAJOR for breaking changes, MINOR for new principles/sections, PATCH for clarifications. Simplicity is enforced: unnecessary complexity is rejected. Rationale: Predictable versioning and simplicity reduce risk and improve developer velocity.

### VI. Performance

- Rendering Performance: Component re-renders, reconciliation optimization
- Bundle Optimization: Code splitting, tree shaking, dynamic imports
- Memory Management: Memory leaks, cleanup patterns, resource management,efficient state management
- Network Performance: Lazy loading, prefetching, caching strategies
- Core Web Vitals: LCP, FID, CLS optimization for React apps
- Profiling Tools: React DevTools Profiler, Chrome DevTools, Lighthouse
- Advanced React Pattern: Concurrent features, Suspense, error boundaries, context optimization
- Rendering Optimization: React.memo, useMemo, useCallback, virtualization, reconciliation
- Bundle Analysis: Webpack Bundle Analyzer, tree shaking, code splitting strategies

## Technology & Compliance

- Backend: FastAPI (Python), PostgreSQL
- Frontend: React, Tailwind CSS and/or Material UI (dynamic theme support) responsive web design support mobile, tablet and desktop
- Authentication: JWT/OAuth2, biometric integration, optional MFA
- Database: PostgreSQL
- Deployment: Docker
- Reporting: Apache Superset, Metabase
- API Documentation: Swagger/OpenAPI
- Directory structure MUST separate backend, frontend, database, reporting, and config
- All code MUST comply with enterprise security standards and best practices
- Performance: Asynchronous backend, efficient queries, frontend code splitting, scalable Docker deployment
- Compliance: Adhere to data protection and privacy regulation

## Development Workflow

- Always create a virtual environment and use uv as package manager. create requirements.txt and always use the virtual environment to install and run any dependencies
- Always fix all lint,pydantic errors
- All code changes require peer review and security validation
- Automated tests MUST pass before merge
- Code reviews verify compliance with principles and technology stack
- Regular penetration testing and code audits
- Documentation (API, architecture, security) MUST be maintained and auto-generated
- Dynamic theme support in frontend is required
- Reporting integrations MUST be tested and secured

## Governance

This constitution supersedes all other practices. Amendments require documentation, approval, and migration plan. Versioning follows semantic rules. All PRs/reviews MUST verify compliance. Complexity MUST be justified. Compliance reviews are scheduled quarterly. Use runtime guidance docs for development reference.

**Version**: 1.1.0 | **Ratified**: TODO(RATIFICATION_DATE): Original adoption date required | **Last Amended**: 2025-09-27