"""
Main FastAPI application for AI Video Editor backend.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings, create_directories
from app.models.schemas import HealthResponse, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    print("🚀 Starting AI Video Editor API...")
    print(f"📦 Version: {settings.app_version}")
    print(f"🤖 LLM Provider: {settings.llm_provider}")
    print(f"🎯 Model: {settings.llm_model}")

    # Create necessary directories
    create_directories()

    yield

    # Shutdown
    print("👋 Shutting down AI Video Editor API...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="FastAPI backend for AI-powered video editing with chat-based subtitle generation",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Mount static files for serving videos
app.mount(
    "/uploads",
    StaticFiles(directory=str(settings.upload_dir)),
    name="uploads"
)
app.mount(
    "/outputs",
    StaticFiles(directory=str(settings.output_dir)),
    name="outputs"
)
app.mount(
    "/temp",
    StaticFiles(directory=str(settings.temp_dir)),
    name="temp"
)


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content=ErrorResponse(
            error="Not Found",
            detail=f"The requested resource was not found: {request.url.path}",
            status_code=404
        ).model_dump()
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Please try again later.",
            status_code=500
        ).model_dump()
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Video Editor API",
        "version": settings.app_version,
        "docs": "/api/docs",
        "health": "/api/health"
    }


# Health check endpoint
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


# Import and include routers
from app.api.routes import upload, chat, export, silence

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(export.router, prefix="/api", tags=["Export"])
app.include_router(silence.router, tags=["Silence"])


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
