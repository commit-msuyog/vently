from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.users import router as users_router

app = FastAPI(
    title=settings.app_name,
    description="An open-source job application automation platform.",
    version=settings.app_version,
    debug=settings.debug,
)

# Register API routers
app.include_router(
    users_router,
    prefix="/api/v1",
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Vently API",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
    }