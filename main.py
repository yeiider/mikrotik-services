from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.routers import metrics, health, mikrotik
from app.services.collector_service import collector_service
from app.core.config import settings
from app.core.database import influx_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await collector_service.start()
    yield
    # Shutdown
    await collector_service.stop()
    influx_db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microservicio de alto rendimiento para métricas MikroTik",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Middleware
from app.core.security import SecurityMiddleware
app.add_middleware(SecurityMiddleware)

# Routers
app.include_router(metrics.router, prefix=f"{settings.API_V1_STR}/metrics", tags=["Metrics"])
app.include_router(health.router, prefix=f"{settings.API_V1_STR}/metrics", tags=["Health"])
app.include_router(mikrotik.router, prefix=f"{settings.API_V1_STR}/mikrotik", tags=["MikroTik"])

@app.get("/")
async def root():
    return {
        "service": settings.PROJECT_NAME,
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/metrics/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
