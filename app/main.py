import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, List

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.v1.api import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Lifespan setup (introduced in FastAPI 0.95.0+)
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle event handler for application startup and shutdown.
    """
    # Startup operations
    logger.info("Starting up the TOC Builder API")

    # Add any startup initialization here, like DB connections

    yield  # This is where the app runs

    # Shutdown operations
    logger.info("Shutting down the TOC Builder API")

    # Add any cleanup operations here, like closing DB connections


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-based table of contents extraction API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to track request processing time.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with user-friendly messages.
    """
    error_detail: List[Dict] = []
    for error in exc.errors():
        error_detail.append(
            {
                "loc": error.get("loc", []),
                "msg": error.get("msg", ""),
                "type": error.get("type", ""),
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": error_detail},
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with basic service information.
    """
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "status": "active",
        "docs": "/docs",
    }


if __name__ == "__main__":
    """
    Run the application directly using Uvicorn.
    For production, use:
    $ uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    """
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Set to False in production
        log_level="info",
    )
