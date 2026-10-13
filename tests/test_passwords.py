import pytest

from src.security.passwords import hash_password, verify_password


@pytest.fixture
def password_hash() -> str:
    """Create a password hash for use in tests."""
    return hash_password("NovaStore-Test-2026")


def test_hash_password_does_not_return_plaintext(
    password_hash: str,
) -> None:
    assert password_hash != "NovaStore-Test-2026"


def test_verify_password_accepts_correct_password(
    password_hash: str,
) -> None:
    assert verify_password("NovaStore-Test-2026", password_hash)


def test_verify_password_rejects_incorrect_password(
    password_hash: str,
) -> None:
    assert not verify_password("Wrong-Password", password_hash)


def test_hash_password_rejects_empty_password() -> None:
    with pytest.raises(ValueError, match="Password must not be empty."):
        hash_password("")


def test_verify_password_rejects_empty_inputs(
    password_hash: str,
) -> None:
    assert not verify_password("", password_hash)
    assert not verify_password("NovaStore-Test-2026", "")
