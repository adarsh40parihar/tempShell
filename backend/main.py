import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from utils.config import settings
from utils.database import init_db
from routers.auth import router as auth_router
from routers.shell import router as shell_router
import controllers.shell_controller as shell_controller

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initializing database...")
    init_db()
    # Start background task: kills user containers idle for >10 minutes
    cleanup_task = asyncio.create_task(shell_controller.cleanup_idle_containers())
    logger.info("Ready.")
    yield
    cleanup_task.cancel()  # Stop the background task on shutdown
    logger.info("Shutting down.")


app = FastAPI(
    title="TempShell API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(shell_router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve React build as static files (if built)
# Must be last to not override other routes
static_dir = Path(__file__).parent / "frontend" / "build"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")
