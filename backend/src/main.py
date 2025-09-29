"""
Production-ready async FastAPI application with performance optimizations
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
import asyncio
import os

from database_async import async_engine, check_async_database_health
from cache_async import redis_cache
from routers.user import router as user_router
from routers.auth import router as auth_router
from routers.client import router as client_router
from routers.business_unit import router as business_unit_router
from routers.invoice import router as invoice_router
from routers.supplier import router as supplier_router
from routers.reporting import router as reporting_router
from routers.region import router as region_router
from routers.role import router as role_router
from routers.audit import router as audit_router
from routers.currency import router as currency_router
from routers.subcategory import router as subcategory_router
from routers.unit_of_measure import router as unit_of_measure_router
from routers.audit_logs import router as audit_logs_router
from routers.client_settings import router as client_settings_router
from routers.import_errors import router as import_errors_router
from routers.invoice_item import router as invoice_item_router
from routers.screen_permissions import router as screen_permissions_router
from routers.user_management import router as user_management_router
from routers.settings import router as settings_router
from deployment_config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    # Startup
    logger.info("🚀 Starting async FastAPI application...")
    
    # Check database connection
    db_healthy = await check_async_database_health()
    if not db_healthy:
        logger.error("❌ Database health check failed!")
        # Don't fail startup - allow app to run for diagnostics
    else:
        logger.info("✅ Database connection healthy")
    
    # Check Redis connection
    cache_healthy = await redis_cache.health_check()
    if not cache_healthy:
        logger.warning("⚠️ Redis health check failed - caching will be disabled")
    else:
        logger.info("✅ Redis connection healthy")
    
    logger.info("✅ Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("🔄 Shutting down application...")
    
    try:
        # Close database connections
        await async_engine.dispose()
        logger.info("✅ Database connections closed")
        
        # Close Redis connections
        await redis_cache.redis_client.close()
        logger.info("✅ Redis connections closed")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {str(e)}")
    
    logger.info("✅ Application shutdown complete")

# Create optimized FastAPI app
app = FastAPI(
    title="SpendPlatform v2 API (Async Optimized)",
    description="High-performance async API with connection pooling, caching, and monitoring",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Performance middleware
app.add_middleware(
    GZipMiddleware, 
    minimum_size=1000  # Compress responses > 1KB
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=86400,  # Cache preflight for 24 hours
)

# Performance monitoring middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Add performance monitoring and request timing"""
    start_time = time.time()
    
    # Add request ID for tracing
    request_id = f"{int(time.time() * 1000000)}"
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Log slow requests
    if process_time > 1.0:
        logger.warning(
            f"🐌 SLOW REQUEST: {request.method} {request.url.path} "
            f"took {process_time:.2f}s (ID: {request_id})"
        )
    elif process_time > 0.5:
        logger.info(
            f"⚠️ Moderate request: {request.method} {request.url.path} "
            f"took {process_time:.3f}s (ID: {request_id})"
        )
    
    return response

# Global exception handler with structured logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions with proper logging"""
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"💥 UNHANDLED EXCEPTION: {request.method} {request.url.path} "
        f"(ID: {request_id}) - {str(exc)}",
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id
        }
    )

# Comprehensive health check endpoint
@app.get("/health")
async def health_check():
    """
    Comprehensive health check for load balancers and monitoring
    """
    start_time = time.time()
    
    # Check database health
    db_healthy = await check_async_database_health()
    
    # Check Redis health
    cache_healthy = await redis_cache.health_check()
    
    check_time = time.time() - start_time
    
    status_code = 200
    overall_status = "healthy"
    
    if not db_healthy:
        status_code = 503
        overall_status = "unhealthy"
    elif not cache_healthy:
        overall_status = "degraded"
    
    response = {
        "status": overall_status,
        "timestamp": time.time(),
        "check_duration_ms": round(check_time * 1000, 2),
        "services": {
            "database": "ok" if db_healthy else "error",
            "cache": "ok" if cache_healthy else "error"
        },
        "version": "2.1.0"
    }
    
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=response)
    
    return response

# Performance info endpoint
@app.get("/performance-info", include_in_schema=False)
async def performance_info():
    """Get performance and configuration information"""
    import psutil
    import os
    
    process = psutil.Process()
    
    return {
        "process_info": {
            "pid": os.getpid(),
            "cpu_percent": process.cpu_percent(),
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "connections": len(process.connections()),
            "threads": process.num_threads()
        },
        "pool_status": {
            "pool_configured": True,
            "pool_active": True
        }
    }

# Development-only token endpoint (disabled in production)
if settings.ENVIRONMENT == "development":
    @app.post("/token")
    async def dev_login_for_access_token(
        username: str,
        password: str
    ):
        """Development-only token endpoint for testing"""
        # Get test credentials from environment variables
        test_username = os.getenv("DEV_TEST_USERNAME", "testuser")
        test_password = os.getenv("DEV_TEST_PASSWORD", "testpass123")
        
        if username == test_username and password == test_password:
            return {
                "access_token": "dev_test_token_async",
                "token_type": "bearer",
                "client_id": int(os.getenv("DEV_TEST_CLIENT_ID", "1"))
            }
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid test credentials"
            )
else:
    # Production: Remove test endpoint entirely
    logger.info("🔒 Test token endpoint disabled in production mode")

# Include all routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(client_router, prefix="/api/v1")
app.include_router(business_unit_router, prefix="/api/v1")
app.include_router(invoice_router, prefix="/api/v1")
app.include_router(supplier_router, prefix="/api/v1")
app.include_router(reporting_router, prefix="/api/v1")
app.include_router(region_router, prefix="/api/v1")
app.include_router(role_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(currency_router, prefix="/api/v1")
app.include_router(subcategory_router, prefix="/api/v1")
app.include_router(unit_of_measure_router, prefix="/api/v1")
app.include_router(audit_logs_router, prefix="/api/v1")
app.include_router(client_settings_router, prefix="/api/v1")
app.include_router(import_errors_router, prefix="/api/v1")
app.include_router(invoice_item_router, prefix="/api/v1")
app.include_router(screen_permissions_router, prefix="/api/v1")
app.include_router(user_management_router, prefix="/api/v1")
app.include_router(settings_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "SpendPlatform v2 API - Async Optimized",
        "version": "2.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_async:app",
        host="0.0.0.0", 
        port=8001,
        reload=True,
        log_level="info"
    )