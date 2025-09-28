# Data Model Design: Backend (FastAPI, SQLAlchemy)

## Entity Overview

All entities include a `client_id` field for multi-tenancy. PK/FK constraints are enforced. Timestamps, audit fields, and soft deletion flags are included for compliance and traceability.

### Audit Fields Enhancement

- All tables include:
  - created_at
  - updated_at
  - created_by (FK to User)
  - updated_by (FK to User)
  - is_deleted (soft deletion flag)

### Sensitive Data Encryption

- `User.password_hash` uses secure hashing (bcrypt/argon2).
- Sensitive columns (e.g., `Supplier.contact_info`) should be encrypted at rest using field-level encryption.

### Role-Permission Granularity

- `Role.permissions` JSON can be replaced or complemented by a normalized permission table or policy-based access control (PBAC) for fine-grained permissions.

### Client Configuration and Settings

- Add a `ClientSettings` entity:
  - id (PK)
  - client_id (FK)
  - feature_flags (JSON)
  - branding (JSON)
  - ui_personalisation (JSON)
  - created_at
  - updated_at

### Currency and UnitOfMeasure

- `Currency.code` should be globally unique (add unique constraint).
- `UnitOfMeasure` can include conversion_factor (optional) for unit conversions.

### Composite Primary Keys or Unique Indexes

- For multi-tenancy, consider composite keys or unique indexes scoped per `client_id`:
  - `Invoice.invoice_number` (unique per client)
  - `Supplier.name` or `Supplier.contact_info` (unique per client)
  - Category names (unique per client)
- Composite PKs or unique filtered indexes strengthen tenant data isolation and integrity.

### 1. Client

- id (PK)
- name
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 2. User

- id (PK)
- username (unique)
- email (unique)
- password_hash
- roles (many-to-many with Role)
- client_id (FK to Client)
- personalisation (JSON: theme, i18n, etc.)


**Note**: User model currently does NOT inherit from AuditMixin (missing audit fields: created_at, updated_at, created_by, updated_by, is_deleted). This should be added for compliance.

### 3. Role

- id (PK)
- name (e.g., superadmin, client_admin, user)
- permissions (JSON)
- users (many-to-many relationship with User)
- screen_permissions (relationship to RoleScreenPermission)
- created_at (AuditMixin)
- updated_at (AuditMixin)
- created_by (FK to User, AuditMixin)
- updated_by (FK to User, AuditMixin)
- is_deleted (soft deletion flag, AuditMixin)

### 4. BusinessUnit

- id (PK)
- name
- code
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 5. Region

- id (PK)
- name
- code
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 6. Supplier

- id (PK)
- name
- contact_info
- region_id (FK)
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 7. Invoice

- id (PK)
- invoice_number
- date
- supplier_id (FK)
- business_unit_id (FK)
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 8. InvoiceItem

- id (PK)
- invoice_id (FK)
- item_number
- type
- description
- subcategory_l1_id (FK)
- subcategory_l2_id (FK)
- subcategory_l3_id (FK)
- subcategory_l4_id (FK)
- qty
- unit_of_measure_id (FK)
- currency_id (FK)
- unit_price
- total_amount
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 9. SubCategoryL1/L2/L3/L4

- id (PK)
- name
- parent_id (FK, for L2/L3/L4; null for L1)
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

**Note:**

- The `parent_id` field enables hierarchical relationships between categories. L2, L3, and L4 subcategories reference their parent category (L1, L2, or L3, respectively). L1 categories have `parent_id = null`.
- This structure supports unlimited category depth if needed, but is currently designed for four levels (L1, L2, L3, L4).
- Queries can traverse the hierarchy using parent-child relationships, supporting tree and nested category structures.

### 10. UnitOfMeasure

- id (PK)
- name
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 11. Currency

- id (PK)
- code
- name
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

### 12. Screen

- id (PK)
- name (unique, e.g., "Dashboard", "Invoices", "Users")
- route (unique, e.g., "/dashboard", "/invoices", "/users")
- description (text)
- category (e.g., "Financial", "Admin", "Reporting")
- is_active (boolean, default True)
- role_permissions (relationship to RoleScreenPermission)

- created_at (AuditMixin)
- updated_at (AuditMixin)
- created_by (FK to User, AuditMixin)
- updated_by (FK to User, AuditMixin)
- is_deleted (soft deletion flag, AuditMixin)


- allow_access (boolean, default False)
- created_at (AuditMixin)
- updated_at (AuditMixin)
- created_by (FK to User, AuditMixin)
- updated_by (FK to User, AuditMixin)
- is_deleted (soft deletion flag, AuditMixin)

### 14. RoleScreenPermission

- id (PK)
- role_id (FK to Role)
- screen_id (FK to Screen)
- client_id (FK to Client)
- allow_access (boolean, default False)
- created_at (AuditMixin)
- updated_at (AuditMixin)
- created_by (FK to User, AuditMixin)
- updated_by (FK to User, AuditMixin)
- is_deleted (soft deletion flag, AuditMixin)

### 15. AuditLog

- id (PK)
- user (string)
- client_id (integer, nullable)
- action (string)
- details (string, nullable)
- timestamp (datetime, default utcnow)

**Note**: AuditLog does NOT use AuditMixin (separate from entity audit fields)

### 16. ImportError

- id (PK)
- invoice_id (FK, nullable)
- row_number (int, nullable)
- error_type (string)
- error_message (string)
- error_details (JSON, optional)
- resolved (bool, default False)
- resolved_by (FK to User, nullable)
- resolved_at (timestamp, nullable)
- client_id (FK)
- created_at
- updated_at
- created_by (FK to User)
- updated_by (FK to User)
- is_deleted (soft deletion flag)

## Relationships

- User <-> Role: many-to-many
- Invoice <-> InvoiceItem: one-to-many
- Supplier <-> Region: many-to-one
- SubCategoryL2/L3/L4 reference parent categories
- All entities reference Client for tenant segregation

## Compliance & Audit

- All tables include created_at, updated_at- created_by (FK to User),updated_by (FK to User),is_deleted (soft deletion flag)
- All sensitive actions logged (import, CRUD, config changes)
- Data retention/deletion managed via scheduled jobs and config

## API Contract: Endpoints, Schemas, RBAC

### General Principles

- All endpoints are scoped by `client_id` for multi-tenancy.
- RBAC enforced via JWT/OAuth2 claims and route guards.
- Audit fields auto-populated from JWT claims (user id).
- Soft deletion (`is_deleted`) respected in all queries.

### Endpoints Overview

#### 1. Client

- `GET /clients` (superadmin only)
- `POST /clients` (superadmin only)
- `GET /clients/{id}` (superadmin only)
- `PUT /clients/{id}` (superadmin only)
- `DELETE /clients/{id}` (superadmin only, soft delete)

#### 2. User

- `GET /users` (client_admin, superadmin)
- `POST /users` (client_admin, superadmin)
- `GET /users/{id}` (self, client_admin, superadmin)
- `PUT /users/{id}` (self, client_admin, superadmin) - Uses UserUpdate schema for partial updates
- `PATCH /users/{id}/password` (self, client_admin, superadmin) - Password reset endpoint
- `DELETE /users/{id}` (client_admin, superadmin, soft delete)

**Schemas**:
- `UserBase`: username, email, client_id, personalisation
- `UserCreate`: extends UserBase + password (required)
- `UserUpdate`: all fields optional (username, email, client_id, personalisation, password)
- `UserRead`: extends UserBase + id, roles
- `PasswordReset`: password field only

#### 3. Role

- `GET /roles` (client_admin, superadmin)
- `POST /roles` (client_admin, superadmin)
- `GET /roles/{id}` (client_admin, superadmin)
- `PUT /roles/{id}` (client_admin, superadmin)
- `DELETE /roles/{id}` (client_admin, superadmin)

#### 4. BusinessUnit

- `GET /business-units` (client_admin, user)
- `POST /business-units` (client_admin)
- `GET /business-units/{id}` (client_admin, user)
- `PUT /business-units/{id}` (client_admin)
- `DELETE /business-units/{id}` (client_admin)

#### 5. Region

- `GET /regions` (client_admin, user)
- `POST /regions` (client_admin)
- `GET /regions/{id}` (client_admin, user)
- `PUT /regions/{id}` (client_admin)
- `DELETE /regions/{id}` (client_admin)

#### 6. Supplier

- `GET /suppliers` (client_admin, user)
- `POST /suppliers` (client_admin)
- `GET /suppliers/{id}` (client_admin, user)
- `PUT /suppliers/{id}` (client_admin)
- `DELETE /suppliers/{id}` (client_admin)

#### 7. Invoice

- `GET /invoices` (client_admin, user)
- `POST /invoices` (client_admin, user)
- `GET /invoices/{id}` (client_admin, user)
- `PUT /invoices/{id}` (client_admin, user)
- `DELETE /invoices/{id}` (client_admin)
- `POST /invoices/import` (client_admin, user) [Excel/CSV import]

#### 8. InvoiceItem

- `GET /invoice-items` (client_admin, user)
- `POST /invoice-items` (client_admin, user)
- `GET /invoice-items/{id}` (client_admin, user)
- `PUT /invoice-items/{id}` (client_admin, user)
- `DELETE /invoice-items/{id}` (client_admin)

#### 9. SubCategoryL1/L2/L3/L4

- `GET /categories` (client_admin, user)
- `POST /categories` (client_admin)
- `GET /categories/{id}` (client_admin, user)
- `PUT /categories/{id}` (client_admin)
- `DELETE /categories/{id}` (client_admin)

#### 10. UnitOfMeasure

- `GET /units` (client_admin, user)
- `POST /units` (client_admin)
- `GET /units/{id}` (client_admin, user)
- `PUT /units/{id}` (client_admin)
- `DELETE /units/{id}` (client_admin)

#### 11. Currency

- `GET /currencies` (client_admin, user)
- `POST /currencies` (client_admin)
- `GET /currencies/{id}` (client_admin, user)
- `PUT /currencies/{id}` (client_admin)
- `DELETE /currencies/{id}` (client_admin)

#### 12. ClientSettings

- `GET /settings` (client_admin)
- `PUT /settings` (client_admin)

#### 13. ScreenPermissions

- `GET /screen-permissions` (client_admin, superadmin)
- `POST /screen-permissions` (client_admin, superadmin)
- `GET /screen-permissions/{id}` (client_admin, superadmin)
- `PUT /screen-permissions/{id}` (client_admin, superadmin)
- `DELETE /screen-permissions/{id}` (client_admin, superadmin)

#### 14. ImportErrors

- `GET /import-errors` (client_admin, user)
- `POST /import-errors` (system generated)
- `GET /import-errors/{id}` (client_admin, user)
- `PUT /import-errors/{id}` (client_admin) - Mark as resolved
- `DELETE /import-errors/{id}` (client_admin)

#### 15. Audit

- `GET /audit` (client_admin, superadmin)
- `POST /audit` (system generated)
- `GET /audit/{id}` (client_admin, superadmin)

### Schemas (Pydantic)

- All entities have matching Pydantic schemas for request/response.
- Audit fields (`created_at`, `updated_at`, `created_by`, `updated_by`, `is_deleted`) included in responses.
- Sensitive fields (e.g., `password_hash`, encrypted columns) excluded from responses.
- Enum/choice fields (e.g., roles, currency codes) validated.

### RBAC Matrix

- Superadmin: Full access to all tenants and entities.
- Client Admin: Full access to own tenant, manage users/roles/settings.
- User: CRUD on own data, view-only on reports, limited import.
- Dynamic roles: Permissions managed via roles and/or PBAC tables.

### Reporting Endpoints

- `GET /reports` (client_admin, user)
- `POST /reports` (client_admin: create dynamic report)
- `GET /reports/{id}` (client_admin, user)

### Import/Export Endpoints

- `POST /invoices/import` (client_admin, user)
- `GET /invoices/export` (client_admin, user)

### Audit & Compliance

- All sensitive actions (import, CRUD, config changes) logged via audit endpoints or hooks.
- Data retention/deletion managed via scheduled jobs and config endpoints.

## Logging & Debugging

- All backend services use Python's `logging` module.
- Logging levels: DEBUG, INFO, WARNING, ERROR, CRITICAL.
- Default level: INFO in production, DEBUG in development.
- Log format includes timestamp, log level, module, message, and request context (user, client_id).
- Sensitive data (e.g., passwords, tokens) must never be logged.
- All API endpoints log request/response metadata and errors.
- Import, export, and batch operations log summary and per-row errors.
- Audit logs are stored separately for compliance.
- Logging configuration is managed via environment variables and client settings.

## Implementation Status

### ✅ Completed
- All SQLAlchemy models implemented
- AuditMixin with audit fields (created_at, updated_at, created_by, updated_by, is_deleted)
- All API endpoints implemented with RBAC
- Pydantic schemas for request/response validation
- Multi-tenancy with client_id scoping
- Password hashing with Argon2
- Screen-level permission system
- Import error tracking system
- Comprehensive logging and audit trails

### ⚠️ Current Limitations
1. **User Model Missing Audit Fields**: User model does not inherit from AuditMixin
2. **Partial Update Support**: Recently added UserUpdate schema for proper partial updates
3. **Screen Permissions**: Advanced permission system beyond basic roles
4. **Import Error Resolution**: Tracking and resolution workflow for data import issues

### 🔄 Recent Changes
- Added `UserUpdate` schema for partial user updates (no password required)
- Implemented screen-level permissions system
- Enhanced import error tracking with resolution workflow
- Updated PUT /users/{id} endpoint to use UserUpdate schema
- Added PATCH /users/{id}/password for dedicated password updates

## Next Steps

- Add AuditMixin inheritance to User model
- Implement field-level encryption for sensitive data
- Add composite unique constraints for multi-tenant isolation
- Enhance reporting endpoints with dynamic report generation
- Implement data retention and compliance policies
