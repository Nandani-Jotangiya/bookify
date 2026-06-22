from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.User import User
from app.models.Category import Category
from app.models.Book import Book
from app.security import hash_password, verify_password,is_valid_email
from app.utils.jwt_handler import create_access_token

from app.auth_dependencies import get_current_user
 
router = APIRouter()

templates = Jinja2Templates(directory="templates")



# REGISTER ROUTES
@router.get("/register")
def register_page(request: Request):

    current_user = get_current_user(request)

    if current_user:

        if current_user["role"] == "admin":
            return RedirectResponse(
                url="/admin/dashboard",
                status_code=303
            )

        if current_user["role"] == "user":
            return RedirectResponse(
                url="/user/dashboard",
                status_code=303
            )

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
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "error": "Name is required",
                "email": email
        }
    )
    if not email:
        return {"error": "Email is required"}
    
    if not is_valid_email(email):
        return templates.TemplateResponse (
            request=request,
            name="auth/register.html",
            context={
                "error":"Please enter valid email address",
                "name":name,
                "email":email
            }
        )
    
    if len(password) < 8:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
               "error": "Password must be at least 8 characters",
               "name": name,
               "email": email
        }
    )

    if len(password.encode("utf-8")) > 72:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
               "error": "Password too long (bcrypt supports max 72 bytes)",
               "name": name,
               "email": email
        }
    )
    
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
               "error":"Passwords do not match",
               "name": name,
               "email": email
        }
    )


    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
             "error": "Email already registered",
             "name": name,
             "email": email
        }
    )

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

    current_user = get_current_user(request)

    if current_user:

        if current_user["role"] == "admin":
            return RedirectResponse(
                url="/admin/dashboard",
                status_code=303
            )

        if current_user["role"] == "user":
            return RedirectResponse(
                url="/user/dashboard",
                status_code=303
            )

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html"
    )

@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    
    if not is_valid_email(email) :
        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context= {
                "error":"Invalid email formate"
            }
        )
    


    # Find user by email
    user = db.query(User).filter(User.email == email).first()

    # User not found
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="auth/password_login.html",
            context={
                "error": "User not found",
                "email": email
            }
        )

    # Invalid password
    if not verify_password(password, user.password):
        return templates.TemplateResponse(
            request=request,
            name="auth/password_login.html",
            context={
                "error": "Invalid Password",
                "email": email
            }
        )

    # Create JWT token
    token = create_access_token(
    {
        "user_id": user.id,
        "name": user.name,
        "role": user.role
    }
)

    print("LOGIN SUCCESS")
    print("ROLE =", user.role)

    # Redirect based on role
    if user.role == "admin":
     response = RedirectResponse(
        url="/dashboard",
        status_code=303
    )

    elif user.role == "user":
        response = RedirectResponse(
            url="/user/dashboard",
            status_code=303
        )

    else:
        return {
            "error": f"Unknown role: {user.role}"
        }

    # Store JWT in cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax"
    )

    return response

@router.post("/check-email")
def check_email(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == email).first()

    if user:
        return templates.TemplateResponse(
            request=request,
            name="auth/password_login.html",
            context={
                "email": email
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "email_not_found": True,
            "email": email
        }
    )

# DASHBOARD ROUTES

@router.get("/admin/dashboard")
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db)
):

    # JWT Authentication Check
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Admin Authorization Check
    if current_user["role"] != "admin":
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    total_categories = db.query(Category).count()
    total_books = db.query(Book).count()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "total_categories": total_categories,
            "total_books": total_books,
            "user": current_user
        }   
    )

# LOGOUT ROUTE
@router.get("/logout")
def logout_page():

    response = RedirectResponse(
        url="/login",
        status_code=303
    )

    response.delete_cookie("access_token")

    return response

