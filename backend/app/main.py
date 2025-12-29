from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.routes import classification
import os
import logging
from ml_models import (
    rear_view_integration,
    side_view_integration,
    top_view_integration,
    udder_view_integration,
    side_udder_integration
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Official Type Classification System as per Annex II",
    docs_url=f"{settings.API_V1_STR}/docs",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Events
@app.on_event("startup")
async def startup():
    """Initialize database and ML models at application startup"""
    # Connect to database
    await connect_to_mongo()
    
    logger.info("=" * 60)
    logger.info("APPLICATION STARTUP - Loading ML Models")
    logger.info("=" * 60)
    
    try:
        import time
        total_start = time.time()
        
        # Initialize all ML models sequentially
        logger.info("[1/5] Initializing rear view model...")
        rear_view_integration.initialize_model()
        
        logger.info("[2/5] Initializing side view model...")
        side_view_integration.initialize_model()
        
        logger.info("[3/5] Initializing top view model...")
        top_view_integration.initialize_model()
        
        logger.info("[4/5] Initializing udder view model...")
        udder_view_integration.initialize_model()
        
        logger.info("[5/5] Initializing side-udder view model...")
        side_udder_integration.initialize_model()
        
        total_time = time.time() - total_start
        logger.info("=" * 60)
        logger.info(f"ALL MODELS LOADED SUCCESSFULLY ({total_time:.2f}s)")
        logger.info(f"API Ready: {settings.API_V1_STR}/docs")
        logger.info("=" * 60)
        
        if total_time > 120:
            logger.warning(f"Startup time {total_time:.2f}s exceeds 120s threshold")
        
    except Exception as e:
        logger.exception("CRITICAL: Model initialization failed")
        logger.error("Application cannot start without models")
        raise

@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()


# Health check endpoint for Render
@app.get("/health")
async def health_check():
    """Lightweight health check"""
    return {"status": "healthy", "version": settings.VERSION}


# Routes
app.include_router(classification.router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Animal Type Classification API",
        "version": settings.VERSION,
        "format": "Official Type Evaluation Format (Annex II)",
        "sections": 5,
        "traits": 20,
        "docs": f"{settings.API_V1_STR}/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
