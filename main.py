import sys
import pydantic

# Pydantic v2 Compatibility Polyfill for Svix and other libraries
if not hasattr(pydantic, 'ModelWrapValidatorHandler'):
    try:
        from pydantic.functional_validators import ModelWrapValidatorHandler
        setattr(pydantic, 'ModelWrapValidatorHandler', ModelWrapValidatorHandler)
    except ImportError:
        pass

"""Main application entry point."""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import config
from database import init_db
from api.auth import router as auth_router
from api.profile import router as profile_router
from api.opportunity import router as opportunity_router
from api.tracking import router as tracking_router
from api.webhook import router as webhook_router
from api.educational import router as educational_router
from api.utility import router as utility_router
from api.gamification import router as gamification_router
from api.team import router as team_router
from api.notifications import router as notifications_router
from middleware.error_handler import setup_error_handlers
from middleware.rate_limiter import RateLimiter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    init_db()
    
    # Start background scheduler
    from scheduler import start_scheduler
    scheduler = start_scheduler()
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Background scheduler stopped")


# Create FastAPI application
app = FastAPI(
    title="HackItAll - Opportunity Access Platform",
    description="AI-powered platform for discovering educational and professional opportunities",
    version="1.0.0",
    debug=config.DEBUG,
    lifespan=lifespan
)

# Configure CORS
import os
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimiter, requests_per_minute=100)

# Setup error handlers
setup_error_handlers(app)

# Include routers
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(opportunity_router)
app.include_router(tracking_router)
app.include_router(webhook_router)
app.include_router(educational_router)
app.include_router(utility_router)
app.include_router(gamification_router)
app.include_router(team_router)
app.include_router(notifications_router)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to HackItAll - Your Gateway to Opportunities",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=config.DEBUG)
