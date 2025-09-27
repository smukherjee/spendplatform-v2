# Phase 0: Research for Modern Enterprise-Grade Invoice/Purchase Order App

## 1. FastAPI Multi-Tenant Architecture & Client Data Segregation
- **Decision:** Use SQLAlchemy models with a `client_id` field for all tenant data. Backend routes and queries will filter by `client_id` to ensure strict segregation. Superadmin APIs will allow cross-client access; client admin APIs will be restricted.
- **Rationale:** This approach is scalable, secure, and aligns with SaaS best practices. It supports hierarchical client management and is compatible with PostgreSQL.
- **Alternatives considered:** Separate schemas per client (complex migrations), row-level security (PostgreSQL native, but more complex for app logic).
- **Compliance:** This architecture supports OWASP, NIST SP 800-115, and PTES standards by enforcing strict data segregation, least privilege, secure authentication, and auditable access. All API endpoints will validate input, enforce RBAC, and log sensitive actions. JWT/OAuth2 flows will be reviewed for security best practices, including token integrity, claim validation, and prevention of privilege escalation. Regular vulnerability scans and code reviews will be performed to ensure ongoing compliance.

## 2. PostgreSQL Schema Design for Multi-Tenancy, PK/FK, Retention/Deletion
- **Decision:** Use a single schema with `client_id` in all tables. Enforce PK/FK constraints for invoices, items, suppliers, etc. Data retention/deletion policies will be managed via scheduled jobs and configuration tables.
- **Rationale:** Single schema simplifies migrations and reporting. PK/FK constraints ensure data integrity. Configurable retention supports compliance.
- **Alternatives considered:** Multiple schemas (harder to manage), partitioned tables (for very large scale).

## 3. Secure Import Workflows for Excel/CSV in FastAPI
- **Decision:** Use Pydantic for validation, Pandas for parsing, and custom error reporting. Import endpoint will validate all rows, report errors, and allow correction/re-import. Auto-classification will use DB lookups during import.
- **Rationale:** Pydantic and Pandas are robust and widely used. Custom error reporting improves UX and data quality.
- **Alternatives considered:** Direct DB import (less control), third-party ETL tools (overkill for core app).

## 4. Scalable CRUD Endpoint Patterns in FastAPI
- **Decision:** Use routers for each entity (BusinessUnit, Region, Supplier, Invoice, etc.), with role-based access control. Superadmin, client admin, and user endpoints will be separated by dependency injection and route guards.
- **Rationale:** Modular routers and DI are best practice in FastAPI. RBAC ensures security and maintainability.
- **Alternatives considered:** Monolithic endpoints (less maintainable), GraphQL (not required for current scope).

## 5. User/Role/Client Management Models for Multi-Tenant SaaS
- **Decision:** Use SQLAlchemy models for User, Role, Client, with many-to-many relationships. Roles will include superadmin, client admin, and user. Personalisation and config will be stored per user and per client.
- **Rationale:** Flexible, supports dynamic roles and personalisation. Aligns with enterprise SaaS standards.
- **Alternatives considered:** Flat user table (not scalable), external IAM (adds complexity).

## 6. React Frontend Structure for Multi-Tenant UI, Personalisation, i18n, Config Screens
- **Decision:** Use React context for tenant/client, user, and theme. Use i18n libraries (e.g., react-i18next) for localisation. Config screens will be split into admin and personalisation sections. All screens and reports will respect user and client settings.
- **Rationale:** Context and i18n are standard in React. Separation of config screens improves UX and security.
- **Alternatives considered:** Redux (overkill for current scope), monolithic config (less secure).

## 7. Secure Authentication/Authorisation (JWT/OAuth2, Biometric, MFA)
- **Decision:** Use JWT for session management, OAuth2 for external integrations, and optional biometric/MFA for sensitive actions. FastAPI dependencies will enforce RBAC and tenant separation.
- **Rationale:** JWT/OAuth2 are secure and scalable. Biometric/MFA add enterprise-grade security.
- **Alternatives considered:** Session cookies (less secure), custom auth (reinventing the wheel).
- **Superadmin & client_id impact:**
    - For regular users and client admins, JWTs will encode the `client_id` claim, restricting access to their tenant's data only. All API requests will be filtered by this claim.
    - For superadmin, JWTs will include a special role claim (e.g., `role: superadmin`) and may omit or wildcard the `client_id` claim, allowing cross-client access. Backend route guards will check for superadmin privileges and bypass client_id filtering.
    - OAuth2 flows will similarly issue tokens with appropriate claims. Superadmin tokens will allow access to all tenants, while client admin/user tokens will restrict access to their own client.
    - All flows must ensure that superadmin actions are auditable and that client data segregation is strictly enforced for non-superadmin roles.
    - Security review: Ensure no privilege escalation or leakage of client data via token manipulation or misconfigured claims.

## 8. Reporting Integration (Superset/Metabase) for Dynamic/Admin/User Views
- **Decision:** Integrate Superset/Metabase via secure API endpoints and embedded dashboards. Admins can create dynamic reports; users can view assigned reports. Data access will be filtered by client ID.
- **Rationale:** These tools are proven for enterprise reporting. API integration supports dynamic and secure access.
- **Alternatives considered:** Custom reporting engine (high effort), direct DB queries (less secure).

## 9. Configuration Screen Best Practices (Admin/Personalisation Separation)
- **Decision:** Separate config screens for admin (client/global settings, retention/deletion) and personalisation (user settings, i18n, theme). Superadmin can access all; client admin only their client.
- **Rationale:** Separation improves security and clarity. Supports multi-tenant and personalisation requirements.
- **Alternatives considered:** Unified config (less secure), external config management (adds complexity).

## 10. Database Migration and Seed Strategies for Multi-Tenant SaaS
- **Decision:** Use Alembic for migrations, with seed scripts for initial client, user, and role data. Migrations will support schema evolution and data retention policies.
- **Rationale:** Alembic is standard for SQLAlchemy. Seed scripts ensure consistent onboarding.
- **Alternatives considered:** Manual migrations (error-prone), external migration tools (adds complexity).

## 11. Automated Testing Strategies for Backend and Frontend
- **Decision:** Use pytest for backend (unit, integration, contract tests), React Testing Library/Jest for frontend. TDD enforced by failing tests before implementation.
- **Rationale:** These tools are standard and integrate well with CI/CD.
- **Alternatives considered:** Manual testing (not acceptable), other frameworks (less community support).

## 12. Documentation Automation (Swagger/OpenAPI, User/Developer Guides)
- **Decision:** Use FastAPI's auto-generated Swagger docs for backend APIs. Write user and developer guides in Markdown, with links from the app UI.
- **Rationale:** Swagger is built-in and widely used. Markdown guides are easy to maintain and version.
- **Alternatives considered:** Custom docs (high effort), external doc platforms (adds cost).

## Error Reporting & Debugging: Mobile (React/React Native)

### Best Practices
- Use centralized error boundary components (React `ErrorBoundary`) to catch and report UI errors.
- Integrate with mobile-friendly error reporting services (e.g., Sentry, Bugsnag, Firebase Crashlytics) for real-time error capture and analytics.
- Log errors with context: device info, OS version, app version, user/session, network state.
- Avoid logging sensitive data (PII, credentials) in error payloads.
- Use native logging APIs for device-level issues (console, native modules).
- Provide user-friendly error screens and actionable feedback for recoverable errors.
- Enable remote debugging and source maps for production builds to trace errors to source code.
- Use performance monitoring tools (e.g., Sentry Performance, Firebase Performance) to correlate errors with slow interactions.
- Automate error triage and alerting for critical failures (push notifications, Slack, email).
- Regularly review error logs and crash reports to prioritize fixes and improve UX.

### Implementation Recommendations

- Add error boundary wrappers to all major screens/components.
- Configure Sentry/Bugsnag/Firebase for mobile error reporting (DSN, environment, release).
- Use custom hooks for error logging and reporting in React Native.
- Sync error logs with backend audit/compliance systems if required.
- Document error handling and logging strategy in developer guides.

## Next Steps

- Research each topic above and document findings, decisions, and rationale in this file.
- Resolve all unknowns before moving to Phase 1 design.
