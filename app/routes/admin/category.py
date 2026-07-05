from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.csrf import verify_csrf_or_redirect
from app.core.dependencies import get_admin_user
from app.core.templates import render_template
from app.database import get_db
from app.models.Book import Book
from app.models.Category import Category
from app.models.IssuedBook import IssuedBook

router = APIRouter()


@router.get("/categories")
def category_page(request: Request, db: Session = Depends(get_db)):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    categories = db.query(Category).all()

    return render_template(request, "admin/categories.html", categories=categories)


@router.get("/categories/add")
def add_category_page(request: Request):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    return render_template(request, "admin/add_categories.html")


@router.post("/categories/add")
def save_category(
    request: Request,
    name: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    name = name.strip()

    if not name:
        return render_template(
            request,
            "admin/add_categories.html",
            error="Category name is required",
        )

    existing_category = db.query(Category).filter(Category.name == name).first()

    if existing_category:
        return render_template(
            request,
            "admin/add_categories.html",
            error="Category already exists",
            name=name,
        )

    category = Category(name=name)

    db.add(category)
    db.commit()

    return RedirectResponse(url="/categories", status_code=303)


@router.get("/categories/edit/{id}")
def edit_category_page(id: int, request: Request, db: Session = Depends(get_db)):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    category = db.query(Category).filter(Category.id == id).first()

    if not category:
        return RedirectResponse(url="/categories", status_code=303)

    return render_template(request, "admin/edit_category.html", category=category)


@router.post("/categories/edit/{id}")
def update_category(
    request: Request,
    id: int,
    name: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    category = db.query(Category).filter(Category.id == id).first()

    if category:
        category.name = name
        db.commit()

    return RedirectResponse(url="/categories", status_code=303)


@router.post("/categories/delete/{id}")
def delete_category(
    id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    category = db.query(Category).filter(Category.id == id).first()

    if category:
        books_in_category = db.query(Book).filter(Book.category_id == id).count()

        if books_in_category > 0:
            categories = db.query(Category).all()
            return render_template(
                request,
                "admin/categories.html",
                categories=categories,
                error="Cannot delete a category that has books assigned to it.",
            )

        issued_in_category = (
            db.query(IssuedBook)
            .join(Book, Book.id == IssuedBook.book_id)
            .filter(
                Book.category_id == id,
                IssuedBook.status == IssuedBook.STATUS_ISSUED,
            )
            .count()
        )

        if issued_in_category > 0:
            categories = db.query(Category).all()
            return render_template(
                request,
                "admin/categories.html",
                categories=categories,
                error="Cannot delete a category that has books currently issued to members.",
            )

        db.delete(category)
        db.commit()

    return RedirectResponse(url="/categories", status_code=303)
