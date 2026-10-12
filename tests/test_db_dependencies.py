from unittest.mock import MagicMock, patch

from src.db.dependencies import get_db


@patch("src.db.dependencies.SessionLocal")
def test_get_db_yields_session_and_closes_it(mock_session_local):
    mock_session = MagicMock()
    mock_session_local.return_value = mock_session

    db_generator = get_db()
    yielded_session = next(db_generator)

    assert yielded_session is mock_session

    try:
        next(db_generator)
    except StopIteration:
        pass

    mock_session.close.assert_called_once_with()
