from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.api.v1 import auth, shell
from app.db.database import init_db
from app.services.k8s_service import K8sService
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database...")
    init_db()
    
    # Cleanup old shell pods
    logger.info("Cleaning up old shell pods...")
    k8s_service = K8sService()
    k8s_service.cleanup_old_pods()
    
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title="TempShell API",
    version="2.0.0",
    description="Secure temporary shell service with Kubernetes isolation",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(shell.router, prefix="/api/v1/shell", tags=["Shell"])

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {
        "status": "healthy",
        "service": "tempshell-api",
        "version": "2.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TempShell API",
        "version": "2.0.0",
        "docs": "/api/docs" if settings.ENVIRONMENT == "development" else None
    }
