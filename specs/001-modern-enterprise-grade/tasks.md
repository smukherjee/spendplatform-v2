# Tasks: Modern Enterprise-Grade Invoice/PO App

## Setup & Prerequisites

T001. [ ] Initialize Python/React project structure and virtual environment (if not done)
T002. [ ] Install all backend dependencies (FastAPI, SQLAlchemy, Alembic, Pandas, argon2-cffi, python-jose, psycopg2-binary)
T003. [ ] Install frontend dependencies (React, react-i18next, error boundary, Sentry/Bugsnag/Firebase Crashlytics)
T004. [ ] Configure PostgreSQL database and Alembic migrations
T005. [ ] Set up linting and formatting tools for Python and JS/TS

## Data Model & Core Entities [P]

T006. [P] Create SQLAlchemy models for all entities (User, Client, Role, BusinessUnit, Region, Supplier, Invoice, InvoiceItem, SubCategoryL1-L4, UnitOfMeasure, Currency, ImportError, ClientSettings)
T007. [P] Write Pydantic schemas for all entities
T008. [P] Implement Alembic migration scripts and apply to DB

## API Contracts & Endpoints

T009. [ ] Define OpenAPI contracts for all endpoints (CRUD, import, reporting, config)
T010. [ ] Scaffold FastAPI routers for each entity and endpoint
T011. [ ] Implement CRUD endpoints for all entities
T012. [ ] Implement import endpoint for Excel/CSV (validation, error reporting)
T013. [ ] Implement reporting endpoints (Superset/Metabase integration)
T014. [ ] Implement config endpoints (ClientSettings, personalisation)

## Authentication & RBAC

T015. [ ] Implement JWT/OAuth2 authentication and session management
T016. [ ] Add role-based access control (superadmin, client admin, user)
T017. [ ] Enforce multi-tenancy and client_id filtering in all endpoints

## Integration & Middleware

T018. [ ] Integrate logging and error reporting (Python logging, audit logs)
T019. [ ] Set up frontend error boundaries and connect to Sentry/Bugsnag/Firebase
T020. [ ] Implement frontend context for tenant/client, user, theme, i18n
T021. [ ] Connect frontend to backend APIs

## Testing [P]

T022. [P] Write contract tests for all API endpoints (pytest)
T023. [P] Write integration tests for user scenarios and edge cases
T024. [P] Write frontend unit and integration tests (React Testing Library/Jest)

## Documentation & Polish [P]

T025. [P] Generate and review Swagger/OpenAPI docs
T026. [P] Write user and developer guides in Markdown
T027. [P] Review and improve code quality, performance, and security

## Parallel Execution Guidance

- Tasks marked [P] can be executed in parallel (e.g., model creation, tests, documentation)
- Sequential tasks should follow dependency order (setup → models → endpoints → integration → polish)

## Dependency Notes

- Setup tasks (T001-T005) must be completed before core, API, and integration tasks
- Data model tasks (T006-T008) before API implementation (T009-T014)
- Authentication/RBAC (T015-T017) before integration and testing
- Testing and documentation can run in parallel after core implementation

---
Feature directory: `/specs/001-modern-enterprise-grade/`
All tasks are actionable and ready for execution by an LLM agent.
