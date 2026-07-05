from fastapi import Request

from app.utils.jwt_handler import decode_access_token


def get_current_user(request: Request):
    """Read JWT from cookie and return payload, or None if missing/invalid."""
    token = request.cookies.get("access_token")

    if not token:
        return None

    return decode_access_token(token)


def get_admin_user(request: Request):
    """Return user payload only if logged in with admin role."""
    current_user = get_current_user(request)

    if not current_user or current_user.get("role") != "admin":
        return None

    return current_user


def get_logged_in_user(request: Request):
    """Return user payload for any authenticated user (admin or user role)."""
    current_user = get_current_user(request)

    if not current_user:
        return None

    return current_user
