# Frontend-Backend Integration Setup

## Overview
This document describes the complete setup for linking the frontend with both sync and async backend servers, including backup configurations and easy switching between server types.

## Server Configuration

### Async Server (Default - Recommended)
- **Port**: 8001
- **Features**: 
  - Redis caching for enhanced performance
  - Async/await operations throughout
  - Performance monitoring headers
  - 43+ optimized endpoints across 19 routers
  - Advanced error handling and logging
- **API Prefix**: `/api/v1`
- **Test Credentials**: `superadmin/superadmin123`

### Sync Server (Backup - Traditional) 
- **Port**: 8000
- **Features**: Traditional synchronous operations
- **API Prefix**: None (direct endpoints)
- **Test Credentials**: `user/user123`

## File Structure

### Main API Services
- `api.ts` - **UPDATED**: Now connects to async server by default
- `api-async.ts` - Dedicated async server configuration
- `api-sync-backup.ts` - **BACKUP**: Original sync server configuration

### Entity Services
- `apiEntities.ts` - **UPDATED**: Now uses async endpoints with `/api/v1` prefix
- `apiEntities-sync-backup.ts` - **BACKUP**: Original sync endpoints

### Configuration Management
- `serverConfig.ts` - Server switching utilities and configuration management
- `.env` - **DEFAULT**: Async server configuration
- `.env.async` - Async server environment template
- `.env.sync` - Sync server environment template

## Quick Start

### 1. Start the Async Server (Backend)
```bash
cd backend
uvicorn main_async:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Start the Frontend
```bash
cd frontend
npm start
```

The frontend will automatically connect to the async server on port 8001.

### 3. Test the Connection
Open browser console and run:
```javascript
import { checkServerHealth } from './services/api';
checkServerHealth();
```

## Switching Between Servers

### Method 1: Environment Variables (Recommended)
1. **To use Async Server (Default)**:
   ```bash
   cp .env.async .env
   npm start
   ```

2. **To use Sync Server**:
   ```bash
   cp .env.sync .env
   npm start
   ```

### Method 2: Direct Import Changes
1. **For Async Server**: Use current `api.ts` and `apiEntities.ts`
2. **For Sync Server**:
   - Import from `api-sync-backup.ts`
   - Import from `apiEntities-sync-backup.ts`

### Method 3: Configuration Utilities
```javascript
import serverConfig from './services/serverConfig';

// Display current configuration
serverConfig.displayCurrentConfig();

// Check both servers
const status = await serverConfig.checkBothServers();
console.log('Server Status:', status);

// Get instructions for switching
serverConfig.switchToAsyncServer();
serverConfig.switchToSyncServer();
```

## API Endpoints Comparison

### Async Server Endpoints (with /api/v1 prefix)
- Authentication: `/api/v1/auth/token`
- Users: `/api/v1/users`
- Clients: `/api/v1/clients`
- Business Units: `/api/v1/business-units`
- Invoices: `/api/v1/invoices`
- Suppliers: `/api/v1/suppliers`
- Regions: `/api/v1/regions`
- Roles: `/api/v1/roles`
- Currencies: `/api/v1/currencies`
- Subcategories: `/api/v1/subcategories`
- Units of Measure: `/api/v1/units-of-measure`
- **Enhanced Endpoints** (Async Only):
  - Audit Logs: `/api/v1/audit-logs`
  - Client Settings: `/api/v1/client-settings`
  - Import Errors: `/api/v1/import-errors`
  - Invoice Items: `/api/v1/invoice-items`
  - Screen Permissions: `/api/v1/screen-permissions`
  - User Management: `/api/v1/user-management`
  - Reports: `/api/v1/reports`

### Sync Server Endpoints (direct)
- Authentication: `/token`
- Users: `/users`
- Clients: `/clients`
- Business Units: `/business-units`
- Invoices: `/invoices`
- Suppliers: `/suppliers`
- Regions: `/regions`
- Roles: `/roles`
- Currencies: `/currencies`
- Subcategories: `/subcategories`
- Units of Measure: `/units-of-measure`

## Testing Credentials

### Async Server
- **Superadmin**: `superadmin/superadmin123`
- **Features**: Access to all enhanced async endpoints

### Sync Server  
- **User**: `user/user123`
- **Client Admin**: `clientadmin/clientadmin123`
- **Superadmin**: `superadmin/superadmin123`

## Performance Benefits of Async Server

1. **Redis Caching**: 
   - 60s cache for volatile data (users, sessions)
   - 300s cache for semi-static data (clients, roles)
   - 3600s cache for static data (currencies, regions)

2. **Async Operations**: Non-blocking I/O for better concurrency

3. **Performance Headers**: Cache status and TTL information in responses

4. **Enhanced Logging**: Detailed request/response logging with performance metrics

5. **Advanced Error Handling**: Comprehensive error responses with detailed debugging information

## Troubleshooting

### Server Connection Issues
1. **Check server status**:
   ```bash
   # Async server
   curl http://localhost:8001/health
   
   # Sync server  
   curl http://localhost:8000/health
   ```

2. **Verify environment variables**:
   ```javascript
   console.log('API Base URL:', process.env.REACT_APP_API_BASE_URL);
   console.log('Server Type:', process.env.REACT_APP_SERVER_TYPE);
   ```

3. **Check console logs**: Look for async server connection messages with ⚡ emoji

### Authentication Issues
1. **Clear stored tokens**:
   ```javascript
   sessionStorage.clear();
   ```

2. **Test login**:
   ```javascript
   import { createTestToken } from './services/api';
   createTestToken();
   ```

### API Endpoint Issues
1. **Verify endpoint format**: Async server requires `/api/v1` prefix
2. **Check server logs**: Both servers provide detailed request logging
3. **Use browser network tab**: Inspect actual API calls being made

## Migration Notes

### From Sync to Async
- All endpoints now require `/api/v1` prefix
- Update test credentials to `superadmin/superadmin123`
- Enable Redis caching features
- Update timeout to 10000ms for async operations

### From Async to Sync  
- Remove `/api/v1` prefix from all endpoints
- Update test credentials to `user/user123`
- Disable caching features
- Reduce timeout to 5000ms for sync operations

## Development Workflow

1. **Default Development**: Use async server for enhanced performance and features
2. **Legacy Testing**: Switch to sync server when testing legacy compatibility
3. **Performance Comparison**: Use both servers to compare response times and caching benefits
4. **Feature Development**: Develop new features on async server for full functionality

## Next Steps

1. **Frontend Integration**: The frontend is now fully configured for async server
2. **Testing**: Verify all CRUD operations work with both servers
3. **Performance Monitoring**: Monitor cache hit rates and response times
4. **Feature Enhancement**: Leverage async-only endpoints for advanced functionality

## Support

For issues or questions:
1. Check server logs in terminal where uvicorn is running
2. Check browser console for detailed API request/response logging
3. Use the server configuration utilities in `serverConfig.ts` for diagnostics
4. Verify both servers are running on correct ports (8000 sync, 8001 async)