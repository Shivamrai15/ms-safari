from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.database import init_db
from src.config import settings
from src.routes import services, status

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    print("Database initialized successfully")
    yield
    print("Shutting down...")

app = FastAPI(
    title="Maintenance Server API",
    description="API for monitoring service status and health",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(services.router)
app.include_router(status.router)

@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Maintenance Server API",
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
async def detailed_health():
    return {
        "status": "healthy",
        "database": "connected",
        "service": "Maintenance Server API"
    }