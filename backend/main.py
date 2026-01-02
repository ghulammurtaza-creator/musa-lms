from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import init_db
from app.routers import families, students, teachers, webhook, monitoring

settings = get_settings()

app = FastAPI(
    title="Academy Management System API",
    description="Automated attendance tracking and billing system for tuition academies",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(families.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(teachers.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    print("Database initialized successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Academy Management System API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2026-01-02T00:00:00Z"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
