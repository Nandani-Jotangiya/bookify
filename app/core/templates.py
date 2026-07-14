from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import Response

from app.config import TEMPLATES_DIR
from app.core.csrf import get_csrf_token

templates = Jinja2Templates(directory=TEMPLATES_DIR)


def render_template(request: Request, name: str, **context) -> Response:
    return templates.TemplateResponse(
        request=request,
        name=name,
        context={
            "request": request,
            "csrf_token": get_csrf_token(request),
            **context,
        },
    )