from fastapi import FastAPI

from app.core.config import settings

from app.api.routes.auth import router as auth_router
from app.api.routes.ai import router as ai_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)


# Include routers
app.include_router(auth_router)
app.include_router(ai_router)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} Running"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "debug_mode": settings.DEBUG
    }