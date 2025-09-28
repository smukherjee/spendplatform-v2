"""
Environment-aware configuration for SpendPlatform v2
Supports both single-server and multi-server deployments
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with deployment mode auto-detection"""
    
    # === Deployment Configuration ===
    DEPLOYMENT_MODE: str = "auto"  # auto, single, distributed, kubernetes
    ENVIRONMENT: str = "development"  # development, staging, production
    SERVICE_INSTANCE: str = "default"
    
    # === API Configuration ===
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # === Database Configuration ===
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "spendplatform"
    DATABASE_USER: str = "spenduser"
    DATABASE_PASSWORD: str = "password"
    DATABASE_URL: Optional[str] = None
    
    # === Redis Configuration ===
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URL: Optional[str] = None
    
    # === Security ===
    SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30
    
    # === CORS Configuration ===
    CORS_ORIGINS: List[str] = []
    
    # === Frontend Service Discovery ===
    FRONTEND_URL: str = "http://localhost:3000"
    
    # === Monitoring & Health ===
    ENABLE_MONITORING: bool = True
    HEALTH_CHECK_ENDPOINT: str = "/health"
    METRICS_ENDPOINT: str = "/metrics"
    
    # === File Storage ===
    UPLOAD_DIR: str = "/app/uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # === Logging ===
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"  # Will be adjusted based on deployment mode
    
    model_config = {"env_file": ".env", "case_sensitive": True}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._auto_configure()
    
    def _auto_configure(self):
        """Auto-configure based on environment after initialization"""
        self._detect_deployment_mode()
        self._configure_database()
        self._configure_redis()
        self._configure_cors()
        self._setup_file_storage()
        self._setup_logging()
    
    def _detect_deployment_mode(self):
        """Auto-detect deployment mode from environment"""
        if self.DEPLOYMENT_MODE == "auto":
            if os.getenv("KUBERNETES_SERVICE_HOST"):
                self.DEPLOYMENT_MODE = "kubernetes"
            elif os.getenv("COMPOSE_PROJECT_NAME"):
                if "multi" in os.getenv("COMPOSE_PROJECT_NAME", ""):
                    self.DEPLOYMENT_MODE = "distributed"
                else:
                    self.DEPLOYMENT_MODE = "single"
            elif os.path.exists("/.dockerenv"):
                self.DEPLOYMENT_MODE = "docker"
            else:
                self.DEPLOYMENT_MODE = "local"
    
    def _configure_database(self):
        """Configure database connection based on deployment mode"""
        if not self.DATABASE_URL:
            # Auto-detect database host based on deployment
            if self.DEPLOYMENT_MODE == "kubernetes":
                self.DATABASE_HOST = "database-service"
            elif self.DEPLOYMENT_MODE in ["single", "distributed"]:
                self.DATABASE_HOST = "database"
            elif self.DEPLOYMENT_MODE == "docker":
                self.DATABASE_HOST = os.getenv("DATABASE_HOST", "database")
            
            # Build DATABASE_URL
            self.DATABASE_URL = (
                f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
                f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            )
    
    def _configure_redis(self):
        """Configure Redis connection based on deployment mode"""
        if not self.REDIS_URL:
            # Auto-detect Redis host
            if self.DEPLOYMENT_MODE == "kubernetes":
                self.REDIS_HOST = "redis-service"
            elif self.DEPLOYMENT_MODE == "single":
                self.REDIS_HOST = "redis"
            elif self.DEPLOYMENT_MODE == "distributed":
                # Redis might be on a different server
                self.REDIS_HOST = os.getenv("REDIS_HOST", "redis")
            
            # Build Redis URL
            if self.REDIS_PASSWORD:
                self.REDIS_URL = f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"
            else:
                self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    def _configure_cors(self):
        """Setup CORS origins based on deployment mode"""
        if not self.CORS_ORIGINS:
            base_origins = []
            
            if self.ENVIRONMENT == "development":
                base_origins = [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://localhost:3001",
                    "http://127.0.0.1:3001"
                ]
            
            # Add deployment-specific origins
            if self.DEPLOYMENT_MODE == "single":
                base_origins.extend([
                    "http://localhost",
                    "http://127.0.0.1",
                    "http://gateway",
                    "http://frontend:3000"
                ])
            elif self.DEPLOYMENT_MODE == "distributed":
                # Add frontend service URL
                base_origins.append(self.FRONTEND_URL)
                # Add potential load balancer origins
                base_origins.extend([
                    "http://gateway",
                    "http://load-balancer"
                ])
            elif self.DEPLOYMENT_MODE == "kubernetes":
                base_origins.extend([
                    "http://frontend-service:3000",
                    "http://ingress-controller"
                ])
            
            self.CORS_ORIGINS = list(set(base_origins))  # Remove duplicates
    
    def _setup_file_storage(self):
        """Setup file storage configuration"""
        if self.DEPLOYMENT_MODE in ["local", "development"]:
            # In local development, use relative path from project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.UPLOAD_DIR = os.path.join(project_root, "uploads")
        # For container deployments, keep the default /app/uploads
    
    def _setup_logging(self):
        """Setup logging configuration"""
        if self.DEPLOYMENT_MODE in ["single", "distributed", "kubernetes"]:
            # In containerized environments, log to stdout for container logs
            self.LOG_FILE = "/dev/stdout"
        elif self.DEPLOYMENT_MODE in ["local", "development"]:
            # In local development, use relative path from project root
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.LOG_FILE = os.path.join(project_root, "logs", "app.log")
        
        # Ensure log directory exists (but skip for stdout)
        if self.LOG_FILE != "/dev/stdout":
            log_dir = os.path.dirname(self.LOG_FILE)
            if log_dir:  # Only create directory if there is one
                os.makedirs(log_dir, exist_ok=True)
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_distributed(self) -> bool:
        """Check if running in distributed mode"""
        return self.DEPLOYMENT_MODE in ["distributed", "kubernetes"]
    
    @property
    def database_pool_size(self) -> int:
        """Get appropriate database pool size based on deployment"""
        if self.is_distributed:
            return 20  # Higher pool for distributed
        elif self.DEPLOYMENT_MODE == "single":
            return 10  # Medium pool for single server
        else:
            return 5   # Small pool for development
    
    def get_service_url(self, service_name: str) -> str:
        """Get URL for a service based on deployment mode"""
        service_urls = {
            "local": {
                "frontend": "http://localhost:3000",
                "backend": "http://localhost:8000",
                "database": f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@localhost:5432/{self.DATABASE_NAME}",
                "redis": "redis://localhost:6379"
            },
            "single": {
                "frontend": "http://frontend:3000",
                "backend": "http://backend:8000", 
                "database": self.DATABASE_URL,
                "redis": self.REDIS_URL
            },
            "distributed": {
                "frontend": self.FRONTEND_URL,
                "backend": f"http://{self.API_HOST}:{self.API_PORT}",
                "database": self.DATABASE_URL,
                "redis": self.REDIS_URL
            },
            "kubernetes": {
                "frontend": "http://frontend-service:3000",
                "backend": "http://backend-service:8000",
                "database": self.DATABASE_URL,
                "redis": self.REDIS_URL
            }
        }
        
        return service_urls.get(self.DEPLOYMENT_MODE, {}).get(service_name, "")
    
    def print_config_summary(self):
        """Print configuration summary for debugging"""
        print(f"""
🔧 SpendPlatform v2 Configuration
================================
Deployment Mode: {self.DEPLOYMENT_MODE}
Environment: {self.ENVIRONMENT}
Service Instance: {self.SERVICE_INSTANCE}

🗄️  Database: {self.DATABASE_HOST}:{self.DATABASE_PORT}
🔄 Redis: {self.REDIS_HOST}:{self.REDIS_PORT}
🌐 Frontend: {self.FRONTEND_URL}
🔧 API: {self.API_HOST}:{self.API_PORT}

📊 CORS Origins: {len(self.CORS_ORIGINS)} configured
📁 Upload Dir: {self.UPLOAD_DIR}  
📋 Log File: {self.LOG_FILE}
📊 Monitoring: {'Enabled' if self.ENABLE_MONITORING else 'Disabled'}
================================
        """)


# Global settings instance
settings = Settings()

# Print config on import for debugging
if os.getenv("DEBUG_CONFIG", "false").lower() == "true":
    settings.print_config_summary()