from fastapi import FastAPI


app = FastAPI(
    title="NovaStore API",
    description="AI-powered customer operations platform",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the basic health status of the API."""
    return {"status": "ok"}
