import bcrypt
import re


def hash_password(password: str) -> str:
    """
    Hashes a raw password securely using native bcrypt.
    """
    # 1. Encode the plain text string into bytes
    password_bytes = password.encode("utf-8")

    # 2. Generate a fresh, random salt
    salt = bcrypt.gensalt()

    # 3. Hash the password and decode the resulting bytes back into a database-friendly string
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_password_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against an existing database hash string.
    """
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    # Securely compares the text against the database hash record
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    return re.match(pattern, email) is not None
