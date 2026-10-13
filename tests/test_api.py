from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from src.api.main import app
from src.db.dependencies import get_db


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_health_check_returns_ok():
    mock_session = MagicMock()

    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/health/database")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert response.json() == {"database": "ok"}
    mock_session.execute.assert_called_once()


def test_database_health_check_returns_unavailable():
    mock_session = MagicMock()
    mock_session.execute.side_effect = SQLAlchemyError(
        "Database query failed"
    )

    def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = client.get("/health/database")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 503
    assert response.json() == {
        "detail": {"database": "unavailable"}
    }


def test_unknown_route_returns_404():
    response = client.get("/does-not-exist")

    assert response.status_code == 404
