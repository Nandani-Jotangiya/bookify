from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

SECRET_KEY = "bookify_super_secret_key_2026"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(hours=10)

    payload.update({"exp": expire})

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        print("DECODED =", payload)

        return payload

    except JWTError as e:
        print("JWT ERROR =", e)
        return None
