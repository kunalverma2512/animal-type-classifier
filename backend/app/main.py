from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.routes import classification
import os
import logging

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
    """Initialize database connection (models load on-demand per request)"""
    await connect_to_mongo()
    logger.info("=" * 60)
    logger.info("Application Startup Complete")
    logger.info("Models will load on-demand (512MB RAM safe)")
    logger.info(f"API Docs: {settings.API_V1_STR}/docs")
    logger.info("=" * 60)

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
