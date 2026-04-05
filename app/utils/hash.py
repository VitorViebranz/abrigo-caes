import bcrypt


def _to_bytes(value: str) -> bytes:
    return value.encode("utf-8")


def hash_password(plain_password: str) -> str:
    password_bytes = _to_bytes(plain_password)
    if len(password_bytes) > 72:
        raise ValueError("Password cannot be longer than 72 bytes for bcrypt.")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = _to_bytes(plain_password)
    if len(password_bytes) > 72:
        return False
    try:
        return bcrypt.checkpw(password_bytes, _to_bytes(hashed_password))
    except ValueError:
        return False
