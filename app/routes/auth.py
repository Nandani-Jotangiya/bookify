from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.User import User
from app.security import hash_password, verify_password
 
router = APIRouter()

templates = Jinja2Templates(directory="templates")



# REGISTER ROUTES

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html"
    )

@router.post("/register")
def register_user(
    request: Request,
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

# LOGIN ROUTES

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html"
    )

@router.post("/login")
def login_user(
    request:Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return {"message": "Invalid Email"}

    # FIXED: Corrected 'user.passoword' typo to 'user.password'
    if not verify_password(password, user.password):
        return {"message": "Invalid Password"}


    request.session["user_id"] = user.id
    request.session["role"] = user.role

    return RedirectResponse(
    url="/dashboard",
    status_code=303
)

# DASHBOARD ROUTES

@router.get("/dashboard")
def dashboard_page(request:Request):

    user_id = request.session.get("user_id")

    if not user_id:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse (
        request=request,
        name="user/dashboard.html"
    )


# LOGOUT ROUTE
@router.get("/logout")
def logout_page(request:Request):

    request.session.clear()

    return RedirectResponse(
        url= "/login",
        status_code=303
    )