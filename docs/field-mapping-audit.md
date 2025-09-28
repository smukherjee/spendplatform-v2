# Frontend-Backend Field Mapping Audit

## User Management Field Mappings

### ✅ Frontend User Interface → Backend Schema Alignment

| Frontend Field | Backend Field | Schema | Notes |
|---------------|---------------|---------|-------|
| `id` | `id` | UserRead | Direct mapping |
| `name` | `username` | UserRead | **Display mapping** - Frontend uses `name` for display, maps to `username` |
| `username` | `username` | UserCreate/UserUpdate | Direct mapping for API calls |
| `email` | `email` | UserCreate/UserUpdate/UserRead | Direct mapping |
| `client_id` | `client_id` | UserCreate/UserUpdate/UserRead | Direct mapping |
| `client_name` | N/A | Frontend only | **Resolved field** - Looked up from clients array using `client_id` |
| `roles` | `roles` | UserCreate/UserUpdate/UserRead | Direct mapping - Array of role names |
| `personalisation` | `personalisation` | UserCreate/UserUpdate/UserRead | Direct mapping |
| `password` | `password` | UserCreate/UserUpdate | Direct mapping (creation/updates only) |

### 🔄 Data Flow Mappings

#### 1. User Creation (POST /users)
```typescript
// Frontend Form Data → Backend UserCreate Schema
{
  name: "John Doe"          // Mapped to username
  username: "john.doe"      // Direct mapping
  email: "john@example.com" // Direct mapping  
  client_id: 1              // Direct mapping
  roles: ["user", "admin"]  // Direct mapping
  password: "secret123"     // Direct mapping
  personalisation: {}       // Direct mapping
}

// Becomes API payload:
{
  username: "john.doe",     // From frontend name/username
  email: "john@example.com",
  client_id: 1,
  roles: ["user", "admin"],
  password: "secret123",
  personalisation: {}
}
```

#### 2. User Updates (PUT /users/:id)  
```typescript
// Frontend Edit Data → Backend UserUpdate Schema
{
  name: "John Updated"       // Mapped to username
  email: "john.new@example.com"
  client_id: 2
  roles: ["admin"]
  // password omitted for inline edits
}

// Becomes API payload:
{
  username: "John Updated",   // From frontend name
  email: "john.new@example.com",
  client_id: 2, 
  roles: ["admin"]
  // personalisation: null (if not provided)
}
```

#### 3. API Response Processing (UserRead → Frontend Display)
```typescript
// Backend UserRead Response
{
  id: 1,
  username: "john.doe",
  email: "john@example.com", 
  client_id: 1,
  roles: ["user", "admin"],
  personalisation: {}
}

// Processed for Frontend Display:
{
  id: 1,
  name: "john.doe",          // Mapped from username
  username: "john.doe",      // Direct mapping
  email: "john@example.com",
  client_id: 1,
  client_name: "Client ABC", // Resolved from clients lookup
  roles: ["user", "admin"],
  personalisation: {}
}
```

### 🏛️ Column Definitions vs API Fields

| Column Field | Editor Field | API Send Field | API Response Field |
|-------------|-------------|---------------|-------------------|
| `field="name"` | `name` → `username` | `username` | `username` → `name` |
| `field="email"` | `email` | `email` | `email` |
| `field="client_id"` | `client_id` | `client_id` | `client_id` |
| `field="roles"` | `roles` | `roles` | `roles` |

### 🔧 Processing Functions

#### User Load Processing (`loadUsers`)
```typescript
const processedUser = {
  id: user.id,
  name: user.username,        // ← KEY MAPPING
  username: user.username,    
  email: user.email,
  client_id: user.client_id,
  client_name: client?.name || `Client ${user.client_id}`, // ← RESOLVED
  personalisation: user.personalisation,
  roles: user.roles || []
};
```

#### User Creation Processing (`saveNewUser`, `saveUser`)
```typescript
const userCreateData = {
  username: (user.username || user.name)?.trim(), // ← MAPPED FROM FRONTEND
  email: user.email?.trim(),
  password: user.password,
  client_id: parseInt(user.client_id?.toString() || '0'),
  personalisation: user.personalisation || null,
  roles: user.roles || []
};
```

#### User Update Processing (`onRowEditComplete`)
```typescript
const updateData = {
  username: newData.username || newData.name, // ← MAPPED FROM FRONTEND
  email: newData.email,
  client_id: newData.client_id,
  personalisation: newData.personalisation || null,
  roles: newData.roles || []
};
```

### ✅ Validation & Consistency Checks

#### ✅ Fixed Issues:
1. **Roles field missing** - Added `roles: rowData.roles || []` to `saveNewUser`
2. **Inconsistent field processing** - All user creation/update functions now properly process the response
3. **Client dropdown mapping** - Fixed `field="client_id"` for proper dropdown value binding
4. **Username disappearing** - Fixed by consistent `username` → `name` mapping in all response processing

#### ✅ Current State:
- ✅ User creation includes all required fields
- ✅ User updates handle partial field updates
- ✅ API responses are consistently processed
- ✅ Client names are properly resolved and displayed
- ✅ Role assignments work in both creation and updates
- ✅ Inline editing maintains field consistency

### 🚨 Critical Mappings to Remember

1. **Display vs Storage**: Frontend `name` = Backend `username`
2. **Client Resolution**: Frontend `client_name` = Lookup from `clients[client_id].name`
3. **Role Handling**: Always include `roles: []` as fallback in API calls
4. **Response Processing**: Always map `username` → `name` when processing API responses
5. **Update Consistency**: Use `newData.username || newData.name` for flexibility

### 📝 Schema Alignment Summary

| Backend Schema | Purpose | Frontend Mapping |
|---------------|---------|------------------|
| `UserCreate` | POST /users | ✅ Fully mapped with roles |
| `UserUpdate` | PUT /users/:id | ✅ Fully mapped with roles |  
| `UserRead` | API responses | ✅ Processed to frontend format |
| `PasswordReset` | PATCH /users/:id/password | ✅ Direct mapping |

All field mappings are now consistent and properly handle the frontend display requirements while maintaining backend schema compliance.