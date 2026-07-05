from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.csrf import verify_csrf_or_redirect
from app.core.dependencies import get_current_user
from app.core.security import hash_password, is_valid_email, verify_password
from app.core.templates import render_template
from app.database import get_db
from app.models.User import User
from app.utils.jwt_handler import create_access_token

router = APIRouter()


@router.get("/register")
def register_page(request: Request):
    current_user = get_current_user(request)
    if current_user:
        if current_user["role"] == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        if current_user["role"] == "user":
            return RedirectResponse(url="/user/dashboard", status_code=303)

    return render_template(request, "auth/register.html")


@router.post("/register")
def register_user(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    name = str(name).strip()
    email = str(email).strip()
    password = str(password).strip()
    confirm_password = str(confirm_password).strip()

    if not name:
        return render_template(
            request, "auth/register.html", error="Name is required", email=email
        )
    if not email:
        return render_template(
            request, "auth/register.html", error="Email is required", name=name
        )

    if not is_valid_email(email):
        return render_template(
            request,
            "auth/register.html",
            error="Please enter valid email address",
            name=name,
            email=email,
        )

    if len(password) < 8:
        return render_template(
            request,
            "auth/register.html",
            error="Password must be at least 8 characters",
            name=name,
            email=email,
        )

    if len(password.encode("utf-8")) > 72:
        return render_template(
            request,
            "auth/register.html",
            error="Password too long (bcrypt supports max 72 bytes)",
            name=name,
            email=email,
        )

    if password != confirm_password:
        return render_template(
            request,
            "auth/register.html",
            error="Passwords do not match",
            name=name,
            email=email,
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return render_template(
            request,
            "auth/register.html",
            error="Email already registered",
            name=name,
            email=email,
        )

    hashed_password = hash_password(str(password))

    new_user = User(name=name, email=email, password=hashed_password, role="user")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/login", status_code=303)


@router.get("/login")
def login_page(request: Request):
    current_user = get_current_user(request)
    if current_user:
        if current_user["role"] == "admin":
            return RedirectResponse(url="/admin/dashboard", status_code=303)
        if current_user["role"] == "user":
            return RedirectResponse(url="/user/dashboard", status_code=303)

    return render_template(request, "auth/login.html")


@router.post("/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not is_valid_email(email):
        return render_template(request, "auth/login.html", error="Invalid email format")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        return render_template(
            request,
            "auth/password_login.html",
            error="User not found",
            email=email,
        )

    if not verify_password(password, user.password):
        return render_template(
            request,
            "auth/password_login.html",
            error="Invalid Password",
            email=email,
        )

    token = create_access_token(
        {"user_id": user.id, "name": user.name, "role": user.role}
    )

    if user.role == "admin":
        response = RedirectResponse(url="/admin/dashboard", status_code=303)
    elif user.role == "user":
        response = RedirectResponse(url="/user/dashboard", status_code=303)
    else:
        return render_template(
            request, "auth/login.html", error=f"Unknown role: {user.role}"
        )

    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")

    return response


@router.post("/check-email")
def check_email(
    request: Request,
    email: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    user = db.query(User).filter(User.email == email).first()

    if user:
        return render_template(request, "auth/password_login.html", email=email)

    return render_template(
        request, "auth/login.html", email_not_found=True, email=email
    )


@router.get("/logout")
def logout_page(request: Request):
    request.session.clear()
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("access_token")
    return response
