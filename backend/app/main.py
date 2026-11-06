from fastapi import FastAPI

app = FastAPI(
    title="Vently API",
    description="An open-source job application automation platform.",
    version="0.1.0",
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