from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import hash_password

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/register")
def register_page(request: Request):
    # UNIVERSAL FIX: Explicitly pass both 'request' and 'name' by keyword.
    # This works across older Starlette versions and new FastAPI 0.110+ versions.
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html"
    )


@router.post("/register")
def register_user(
    request:Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):

    name = str(name).strip()
    email = str(email).strip()
    password = str(password).strip()
    confirm_password = str(confirm_password).strip()

    if not name:
        return {"error": "Name is required"}

    if not email:
        return {"error": "Email is required"}

    if len(password) < 8:
        return {"error": "Password must be at least 8 characters"}

    # bcrypt limit (72 BYTES, not characters)
    if len(password.encode("utf-8")) > 72:
        return {"error": "Password too long (bcrypt supports max 72 bytes)"}

    if password != confirm_password:
        return {"error": "Passwords do not match"}

    existing_user = db.query(User).filter(User.email == email).first()

    if existing_user:
        return {"error": "Email already registered"}

    hashed_password = hash_password(str(password))
    
    new_user = User(
        name=name,
        email=email,
        password=hashed_password,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)

@router.get("/login")
def login_page(request: Request):
    # Simply returns a basic text message until you build your login.html template
    return {"message": "Registration successful! Login page coming soon."}
