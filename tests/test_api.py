from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from src.api.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("src.api.routes.health.engine.connect")
def test_database_health_check_returns_ok(mock_connect):
    mock_connection = MagicMock()
    mock_connect.return_value.__enter__.return_value = mock_connection

    response = client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {"database": "ok"}
    mock_connection.execute.assert_called_once()


@patch("src.api.routes.health.engine.connect")
def test_database_health_check_returns_unavailable(mock_connect):
    mock_connect.side_effect = SQLAlchemyError("Database connection failed")

    response = client.get("/health/database")

    assert response.status_code == 503
    assert response.json() == {
        "detail": {"database": "unavailable"}
    }
