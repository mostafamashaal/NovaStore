from fastapi import FastAPI

from src.api.routes.auth import router as auth_router
from src.api.routes.health import router as health_router
from src.api.routes.customers import router as customers_router


app = FastAPI(
    title="NovaStore API",
    description="AI-powered customer operations platform",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(customers_router)
