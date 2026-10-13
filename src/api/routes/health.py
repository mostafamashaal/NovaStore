from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.db.dependencies import get_db


router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    """Return the basic health status of the API."""
    return {"status": "ok"}


@router.get("/health/database")
def database_health_check(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Check whether the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
        return {"database": "ok"}

    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail={"database": "unavailable"},
        )
