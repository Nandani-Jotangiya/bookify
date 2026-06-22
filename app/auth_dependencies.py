from fastapi import Request

from app.utils.jwt_handler import decode_access_token

def get_current_user(request: Request):

    token = request.cookies.get("access_token")

    print("TOKEN =", token)

    if not token:
        return None

    payload = decode_access_token(token)

    print("PAYLOAD =", payload)

    return payload