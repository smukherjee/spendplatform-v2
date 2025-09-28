# ✅ Quick Start: Adding New Screens

## **Essential Steps for Performance-Optimized Screen Development**

### **1. Create Screen Component** 📄
```bash
# Location: /src/screens/YourNewScreen.tsx
```

**Key Requirements:**
- Use `React.memo()` wrapper
- Import only needed PrimeReact components
- Use `useCallback()` for event handlers
- Use `useMemo()` for expensive computations
- Add performance tracking with `performanceTimer`

### **2. Add Lazy Loading** ⚡
```typescript
// In /src/routes.tsx

// Add lazy import
const YourNewScreen = lazy(() => import('./screens/YourNewScreen'));

// Add route with ProtectedRoute wrapper
<Route 
  path="/your-new-screen" 
  element={
    <ProtectedRoute screenRoute="/your-new-screen">
      <YourNewScreen />
    </ProtectedRoute>
  } 
/>
```

### **3. Update Navigation** 🧭
```typescript
// In /src/components/NavBar.tsx

// Add to screens array
const screens = useMemo(() => [
  // ... existing screens
  '/your-new-screen',
], []);

// Add to navigationItems
const navigationItems = useMemo(() => {
  const items = [
    // ... existing items
    { path: '/your-new-screen', label: 'Your New Screen' },
  ];
  return items.filter(item => hasAccess(item.path));
}, [hasAccess]);
```

### **4. Configure Permissions** 🔐
```sql
-- Backend: Add screen permissions
INSERT INTO screen_permissions (screen_route, role, has_access) 
VALUES 
  ('/your-new-screen', 'superadmin', true),
  ('/your-new-screen', 'client_admin', true),
  ('/your-new-screen', 'user', false);
```

### **5. Test Performance** 🧪
```bash
# Build and check bundle size
npm run build

# Analyze bundle (main should stay ~113 kB)
npm run analyze

# Start dev server and test
npm start
```

## **Performance Validation Checklist** ✅

- [ ] Screen loads in separate chunk (not main bundle)
- [ ] Component wrapped with `React.memo()`
- [ ] Event handlers use `useCallback()`
- [ ] Expensive computations use `useMemo()`
- [ ] Only required PrimeReact components imported
- [ ] Navigation appears with proper permissions
- [ ] Loading states and error boundaries work
- [ ] Mobile responsive design verified
- [ ] No performance regressions in build size

## **Quick Templates** 📋

### **Basic Screen Template:**
```typescript
import React, { useState, useCallback, useMemo } from 'react';

const YourScreen = React.memo(() => {
  const [data, setData] = useState([]);
  
  const handleAction = useCallback(() => {
    // Action logic
  }, []);

  return (
    <div className="screen-container">
      {/* Content */}
    </div>
  );
});

YourScreen.displayName = 'YourScreen';
export default YourScreen;
```

### **Common Imports:**
```typescript
// Performance utilities
import { performanceTimer } from '../utils/performance';
import { useAuth } from '../contexts/AuthContext';

// PrimeReact (import only what you need)
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import { Button } from 'primereact/button';
```

## **Backend Development (FastAPI)** 🔗

### **6. Create Async API Endpoint** 🛠️

```python
# Location: /backend/app/routers/your_module.py

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_async_db
from app.models import YourModel, User
from app.schemas import YourSchema, YourCreateSchema, YourUpdateSchema, PaginatedResponse
from app.dependencies import get_current_user
from app.cache import redis_cache
from app.core.logging import get_logger
from typing import List, Optional
import asyncio

logger = get_logger(__name__)
router = APIRouter(prefix="/api/your-module", tags=["your-module"])

@router.get("/", response_model=PaginatedResponse[YourSchema])
async def get_items(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Get paginated list of items with optimized queries"""
    
    # Build cache key for this query
    cache_key = f"items:{current_user.id}:{skip}:{limit}:{search}:{is_active}"
    
    # Try to get from cache first
    cached_result = await redis_cache.get(cache_key)
    if cached_result:
        return cached_result
    
    try:
        # Build query with eager loading and selective columns
        query = select(YourModel).options(
            selectinload(YourModel.creator)  # Eager load to avoid N+1
        ).where(YourModel.created_by == current_user.id)
        
        # Add filters
        if search:
            query = query.where(YourModel.name.ilike(f"%{search}%"))
        if is_active is not None:
            query = query.where(YourModel.is_active == is_active)
        
        # Get total count and paginated results in parallel
        count_query = select(func.count(YourModel.id)).where(
            YourModel.created_by == current_user.id
        )
        if search:
            count_query = count_query.where(YourModel.name.ilike(f"%{search}%"))
        if is_active is not None:
            count_query = count_query.where(YourModel.is_active == is_active)
        
        # Execute queries concurrently
        items_task = db.execute(query.offset(skip).limit(limit))
        count_task = db.execute(count_query)
        
        items_result, count_result = await asyncio.gather(items_task, count_task)
        
        items = items_result.scalars().all()
        total = count_result.scalar()
        
        # Prepare response
        response = PaginatedResponse(
            items=[YourSchema.from_orm(item) for item in items],
            total=total,
            skip=skip,
            limit=limit,
            has_next=skip + limit < total
        )
        
        # Cache result for 5 minutes
        await redis_cache.set(cache_key, response, expire=300)
        
        logger.info(f"Retrieved {len(items)} items for user {current_user.id}")
        return response
        
    except Exception as e:
        logger.error(f"Error retrieving items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve items"
        )

@router.post("/", response_model=YourSchema)
async def create_item(
    item: YourCreateSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Create new item with proper transaction handling"""
    
    try:
        async with db.begin():  # Automatic transaction management
            # Create new item
            db_item = YourModel(
                **item.dict(exclude_unset=True),
                created_by=current_user.id
            )
            db.add(db_item)
            await db.flush()  # Get ID without committing
            
            # Eager load creator for response
            await db.refresh(db_item, ["creator"])
            
            # Add background task for cache invalidation
            background_tasks.add_task(
                invalidate_user_cache, 
                current_user.id
            )
            
            # Add background task for audit logging
            background_tasks.add_task(
                log_item_creation,
                db_item.id,
                current_user.id
            )
            
        logger.info(f"Created item {db_item.id} for user {current_user.id}")
        return YourSchema.from_orm(db_item)
        
    except Exception as e:
        logger.error(f"Error creating item: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create item"
        )

@router.put("/{item_id}", response_model=YourSchema)
async def update_item(
    item_id: int,
    item_update: YourUpdateSchema,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Update item with optimistic locking"""
    
    try:
        async with db.begin():
            # Use select for update to prevent race conditions
            result = await db.execute(
                select(YourModel)
                .options(selectinload(YourModel.creator))
                .where(
                    YourModel.id == item_id,
                    YourModel.created_by == current_user.id
                )
                .with_for_update()
            )
            
            db_item = result.scalar_one_or_none()
            if not db_item:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Item not found"
                )
            
            # Update only provided fields
            update_data = item_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_item, field, value)
            
            await db.flush()
            
            # Background tasks
            background_tasks.add_task(invalidate_user_cache, current_user.id)
            
        logger.info(f"Updated item {item_id} for user {current_user.id}")
        return YourSchema.from_orm(db_item)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item {item_id}: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update item"
        )

@router.get("/batch", response_model=List[YourSchema])
async def get_items_batch(
    item_ids: List[int],
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user)
):
    """Batch retrieve items to reduce query overhead"""
    
    if len(item_ids) > 100:  # Limit batch size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch size cannot exceed 100 items"
        )
    
    try:
        # Single query with IN clause for batch retrieval
        result = await db.execute(
            select(YourModel)
            .options(selectinload(YourModel.creator))
            .where(
                YourModel.id.in_(item_ids),
                YourModel.created_by == current_user.id
            )
        )
        
        items = result.scalars().all()
        return [YourSchema.from_orm(item) for item in items]
        
    except Exception as e:
        logger.error(f"Error batch retrieving items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve items"
        )

# Background task functions
async def invalidate_user_cache(user_id: int):
    """Invalidate all cache entries for a user"""
    await redis_cache.delete_pattern(f"items:{user_id}:*")

async def log_item_creation(item_id: int, user_id: int):
    """Log item creation for audit purposes"""
    logger.info(f"AUDIT: Item {item_id} created by user {user_id}")
```

### **7. Create Optimized Database Model** 🗄️

```python
# Location: /backend/app/models/your_model.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index, text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from typing import Optional

class YourModel(Base):
    __tablename__ = "your_table"
    
    # Primary key with explicit naming
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Indexed columns for fast lookups
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True,
        comment="Item name for display"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        index=True,  # Index for filtering
        server_default=text('true')
    )
    
    # Timestamps with server defaults for better performance
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True  # Index for sorting/filtering by date
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Foreign key with proper indexing
    created_by: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Critical for user-based queries
    )
    
    # Relationships with lazy loading configuration
    creator: Mapped["User"] = relationship(
        "User", 
        back_populates="your_items",
        lazy="select"  # Explicit lazy loading
    )
    
    # Composite indexes for common query patterns
    __table_args__ = (
        # Index for user + active items (most common query)
        Index('idx_user_active', 'created_by', 'is_active'),
        # Index for user + created_at (for sorting)
        Index('idx_user_created', 'created_by', 'created_at'),
        # Index for search functionality
        Index('idx_name_search', 'name', postgresql_using='gin'),
        # Partial index for active items only
        Index('idx_active_items', 'id', postgresql_where=text('is_active = true')),
    )
    
    def __repr__(self) -> str:
        return f"<YourModel(id={self.id}, name='{self.name}', active={self.is_active})>"
```

### **8. Create Optimized Pydantic Schemas** 📋

```python
# Location: /backend/app/schemas/your_schema.py

from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
import re

# Generic type for pagination
T = TypeVar('T')

class YourBaseSchema(BaseModel):
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=255,
        description="Item name",
        example="My Item"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000,
        description="Optional item description"
    )
    is_active: bool = Field(
        default=True,
        description="Whether the item is active"
    )

    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty or whitespace only')
        
        # Remove multiple spaces and trim
        cleaned = re.sub(r'\s+', ' ', v.strip())
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', cleaned):
            raise ValueError('Name contains invalid characters')
            
        return cleaned

    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            v = v.strip()
            if len(v) == 0:
                return None
        return v

    class Config:
        # Optimize JSON serialization
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Allow field population by name or alias
        allow_population_by_field_name = True
        # Validate assignment to prevent data corruption
        validate_assignment = True

class YourCreateSchema(YourBaseSchema):
    """Schema for creating new items"""
    
    @root_validator
    def validate_create_data(cls, values):
        name = values.get('name')
        description = values.get('description')
        
        # Business rule: if no description, generate from name
        if not description and name:
            values['description'] = f"Auto-generated description for {name}"
            
        return values

class YourUpdateSchema(BaseModel):
    """Schema for updating items - all fields optional"""
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=255
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000
    )
    is_active: Optional[bool] = None

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Name cannot be empty or whitespace only')
            return re.sub(r'\s+', ' ', v.strip())
        return v

    class Config:
        validate_assignment = True

class YourSchema(YourBaseSchema):
    """Full schema with all fields including auto-generated ones"""
    id: int = Field(..., description="Unique identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: int = Field(..., description="ID of user who created this item")
    
    # Optional nested creator info (loaded when needed)
    creator: Optional['UserSchema'] = Field(
        None, 
        description="Creator user information"
    )

    class Config:
        orm_mode = True
        # Use enum values for better performance
        use_enum_values = True
        # Optimize JSON encoding
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # Allow population by name for ORM compatibility
        allow_population_by_field_name = True

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    skip: int = Field(..., ge=0, description="Number of items skipped")
    limit: int = Field(..., ge=1, le=1000, description="Maximum items per page")
    has_next: bool = Field(..., description="Whether there are more items")
    
    class Config:
        # Optimize for API responses
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Circular import resolution
from app.schemas.user import UserSchema
YourSchema.model_rebuild()
```

### **9. Add Screen Permissions** 🔐

```python
# Location: /backend/app/routers/permissions.py

@router.post("/screen-permissions")
async def create_screen_permission(
    screen_route: str,
    role: str,
    has_access: bool = True,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_superadmin)
):
    """Add screen permission for role"""
    permission = ScreenPermission(
        screen_route=screen_route,
        role=role,
        has_access=has_access
    )
    db.add(permission)
    db.commit()
    return {"message": "Permission created successfully"}
```

### **9. Async Database Configuration** �

```python
# Location: /backend/app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool, QueuePool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create async engine with optimized connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    # Connection pool configuration for high concurrency
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections during peak load
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections every hour
    # Query optimization
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    future=True,  # Use SQLAlchemy 2.0 style
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects accessible after commit
    autoflush=False,  # Manual control over flushing
    autocommit=False,
)

Base = declarative_base()

# Dependency for getting async database session
async def get_async_db() -> AsyncSession:
    """
    Async database session dependency with proper error handling
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

# Connection health check
async def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False
```

### **10. Redis Cache Configuration** 🗄️

```python
# Location: /backend/app/cache.py

import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AsyncRedisCache:
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,  # Handle binary data
            max_connections=20,
            retry_on_timeout=True,
            socket_keepalive=True,
            socket_keepalive_options={},
            health_check_interval=30,
        )
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with automatic deserialization"""
        try:
            value = await self.redis_client.get(key)
            if value is None:
                return None
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        expire: Optional[int] = None
    ) -> bool:
        """Set value in cache with automatic serialization"""
        try:
            serialized_value = pickle.dumps(value)
            if expire:
                return await self.redis_client.setex(key, expire, serialized_value)
            else:
                return await self.redis_client.set(key, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(await self.redis_client.delete(key))
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = await self.redis_client.keys(pattern)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {str(e)}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(await self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {str(e)}")
            return False

# Global cache instance
redis_cache = AsyncRedisCache()
```

### **11. Database Migration** 🔄

```bash
# Create migration with optimized indexes
cd backend
alembic revision --autogenerate -m "Add optimized your_table with indexes"

# Apply migration
alembic upgrade head

# Verify migration and indexes
alembic current

# Check index creation
psql $DATABASE_URL -c "\\d+ your_table"
```

### **12. Optimized Main App Configuration** 🔧

```python
# Location: /backend/app/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import logging
import time

from app.core.config import settings
from app.database import engine, check_database_health
from app.cache import redis_cache
from app.routers import your_module, auth, permissions
from app.core.logging import setup_logging

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("Starting FastAPI application...")
    
    # Check database connection
    if not await check_database_health():
        logger.error("Database health check failed!")
        raise Exception("Database connection failed")
    
    # Warm up cache connection
    await redis_cache.redis_client.ping()
    logger.info("Cache connection established")
    
    # Create database tables if needed
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")
    
    # Close database connections
    await engine.dispose()
    
    # Close Redis connections
    await redis_cache.redis_client.close()
    
    logger.info("Application shutdown complete")

# Create FastAPI app with optimized configuration
app = FastAPI(
    title="SpendPlatform API",
    description="High-performance API for spend management platform",
    version="2.0.0",
    docs_url="/docs" if settings.DEBUG else None,  # Disable in production
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
    # Response optimization
    generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}",
)

# Add middleware for performance
app.add_middleware(
    GZipMiddleware, 
    minimum_size=1000  # Compress responses > 1KB
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:  # Log requests taking > 1 second
        logger.warning(
            f"Slow request: {request.method} {request.url.path} "
            f"took {process_time:.2f}s"
        )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    db_healthy = await check_database_health()
    
    try:
        await redis_cache.redis_client.ping()
        cache_healthy = True
    except:
        cache_healthy = False
    
    if db_healthy and cache_healthy:
        return {"status": "healthy", "database": "ok", "cache": "ok"}
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "ok" if db_healthy else "error",
                "cache": "ok" if cache_healthy else "error"
            }
        )

# Include routers with versioning
app.include_router(auth.router, prefix="/api/v1")
app.include_router(permissions.router, prefix="/api/v1")
app.include_router(your_module.router, prefix="/api/v1")

# Add startup event for warming up
@app.on_event("startup")
async def warm_up():
    """Warm up critical components"""
    # Pre-load frequently accessed data
    await asyncio.gather(
        redis_cache.redis_client.ping(),
        check_database_health(),
        return_exceptions=True
    )
```

### **12. Add API Tests** 🧪

```python
# Location: /backend/tests/test_your_module.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post(
        "/api/your-module/",
        json={"name": "Test Item", "description": "Test Description"},
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"

def test_get_items():
    response = client.get(
        "/api/your-module/",
        headers={"Authorization": "Bearer test_token"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## **Backend Performance Validation Checklist** ✅

### **🚀 Async & Performance**
- [ ] All endpoints use `async def` with proper `await`
- [ ] AsyncSession used instead of regular Session
- [ ] Connection pooling configured (pool_size=20, max_overflow=30)
- [ ] Redis cache implemented for frequent queries
- [ ] Background tasks used for non-critical operations
- [ ] Proper transaction management with `async with db.begin()`

### **🗄️ Database Optimization**
- [ ] Composite indexes created for common query patterns
- [ ] Eager loading with `selectinload()` to avoid N+1 queries
- [ ] Pagination implemented at query level
- [ ] Batch operations for multiple records
- [ ] Selective column loading where appropriate
- [ ] Database health checks implemented

### **📊 API Design**
- [ ] Pydantic models with proper validation and ORM mode
- [ ] Generic pagination response schema
- [ ] Proper HTTP status codes and error handling
- [ ] API versioning in router prefix
- [ ] OpenAPI documentation (disabled in production)
- [ ] Request/response compression middleware

### **🔒 Security & Reliability**
- [ ] Authentication on all protected endpoints
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention with parameterized queries
- [ ] Rate limiting configured
- [ ] Structured logging with correlation IDs
- [ ] Health check endpoint for load balancers

### **🧪 Testing & Monitoring**
- [ ] Unit tests for all endpoints
- [ ] Integration tests with test database
- [ ] Performance benchmarking with load testing
- [ ] Query profiling and EXPLAIN analysis
- [ ] Response time monitoring (< 200ms for simple queries)
- [ ] Error rate monitoring and alerting

## **Production-Ready Development Commands** 💻

```bash
# Start optimized FastAPI server with multiple workers
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 --worker-connections 1000

# Development with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 \
  --loop uvloop --http httptools

# Database operations
alembic upgrade head                    # Apply migrations
alembic current                        # Check current version
alembic history --verbose             # View migration history

# Performance testing
pytest tests/ -v --cov=app --cov-report=html
locust -f tests/load_test.py --host=http://localhost:8000

# Database query analysis
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM your_table 
  WHERE created_by = 1 AND is_active = true;

# Redis cache monitoring
redis-cli monitor  # Watch cache operations in real-time
redis-cli info     # Check Redis performance stats

# Health and monitoring
curl http://localhost:8000/health      # Check API health
curl -H "Accept-Encoding: gzip" http://localhost:8000/api/v1/your-module/
```

## **Troubleshooting** 🔧

**Screen not lazy loading?**
- Check lazy import syntax: `lazy(() => import('./path'))`

**Bundle size increased?**
- Avoid importing entire libraries
- Check for heavy dependencies in component

**Navigation not showing?**
- Verify screens array in NavBar
- Check backend permissions
- Confirm user role has access

**Performance issues?**
- Add React.memo wrapper
- Memoize event handlers and computations
- Check for object creation in render

**API not working?**
- Check FastAPI server is running on port 8000
- Verify database connection and migrations
- Check authentication headers in requests
- Review API logs for errors

**Database issues?**
- Ensure PostgreSQL is running
- Check connection string in .env
- Verify migration status with `alembic current`
- Check table structure in database

---

**For detailed documentation, see: `DEVELOPMENT.md`**

**Performance results: `PERFORMANCE_TEST_RESULTS.md`**