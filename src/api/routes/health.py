from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter, HTTPException

from src.db.database import engine

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the basic health status of the API."""
    return {"status": "ok"}

@router.get("/health/database")
def database_health_check() -> dict[str, str]:
    """Check whether the database is reachable."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"database": "ok"}

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={"database": "unavailable"},
        )
