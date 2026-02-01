from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.core.database import init_db
from app.routers import (
    families, students, teachers, webhook, monitoring, schedule, oauth,
    test_webhook, sync, test_attendance, auth, assignments, relationships
)
from app.services.meeting_monitor import start_monitoring, stop_monitoring

settings = get_settings()

app = FastAPI(
    title="Academy Management System API",
    description="Automated attendance tracking and billing system for tuition academies",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    redirect_slashes=True
)

# Configure CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(assignments.router)
app.include_router(relationships.router)
app.include_router(families.router, prefix="/api")
app.include_router(students.router, prefix="/api")
app.include_router(teachers.router, prefix="/api")
app.include_router(webhook.router, prefix="/api")
app.include_router(monitoring.router, prefix="/api")
app.include_router(oauth.router, prefix="/api")
app.include_router(sync.router, prefix="/api")
app.include_router(test_attendance.router)
app.include_router(schedule.router)
app.include_router(test_webhook.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database and start monitoring service"""
    await init_db()
    print("Database initialized successfully")
    
    # Start meeting monitoring service
    start_monitoring()
    print("Meeting monitoring service initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop monitoring service on shutdown"""
    stop_monitoring()
    print("Meeting monitoring service stopped")


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
