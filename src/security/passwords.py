from pwdlib import PasswordHash


_password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password for secure storage."""
    if not password:
        raise ValueError("Password must not be empty.")

    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check whether a password matches its stored hash."""
    if not password or not password_hash:
        return False

    return _password_hasher.verify(password, password_hash)
