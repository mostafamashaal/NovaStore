from sqlalchemy import text
from src.db.database import SessionLocal

def test_database_connection():
    db = SessionLocal()

    try:
        result = db.execute(
            text("SELECT current_database(), current_user")
            ).fetchone()

        assert result is not None
        assert result[0] == "novastore"
        assert result[1] == "novastore"

    finally:
        db.close()    
