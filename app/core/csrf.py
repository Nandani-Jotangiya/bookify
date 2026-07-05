import secrets

from fastapi import Request
from fastapi.responses import RedirectResponse

CSRF_SESSION_KEY = "csrf_token"


def get_csrf_token(request: Request) -> str:
    token = request.session.get(CSRF_SESSION_KEY)

    if not token:
        token = secrets.token_urlsafe(32)
        request.session[CSRF_SESSION_KEY] = token

    return token


def verify_csrf_token(request: Request, token: str | None) -> bool:
    session_token = request.session.get(CSRF_SESSION_KEY)

    if not token or not session_token:
        return False

    return secrets.compare_digest(token, session_token)


def verify_csrf_or_redirect(
    request: Request, csrf_token: str | None
) -> RedirectResponse | None:
    if not verify_csrf_token(request, csrf_token):
        return RedirectResponse(url="/login", status_code=403)

    return None
