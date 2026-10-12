from collections.abc import Generator

from sqlalchemy.orm import Session

from src.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a database session and close it after use."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
