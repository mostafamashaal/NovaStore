from fastapi import FastAPI

from src.api.routes.health import router as health_router


app = FastAPI(
    title="NovaStore API",
    description="AI-powered customer operations platform",
    version="0.1.0",
)

app.include_router(health_router)
