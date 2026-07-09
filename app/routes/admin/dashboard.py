from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.context import get_admin_context
from app.core.dependencies import get_admin_user
from app.core.templates import render_template
from app.database import get_db
from app.models.Book import Book
from app.models.BookRequest import BookRequest
from app.models.Category import Category
from app.models.IssuedBook import IssuedBook
from app.models.User import User

router = APIRouter()


@router.get("/admin/dashboard")
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
):
    current_admin = get_admin_user(request)

    if not current_admin:
        return RedirectResponse("/login", status_code=303)

    total_books = db.query(Book).count()

    total_users = db.query(User).count()

    total_categories = db.query(Category).count()

    total_issued_books = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.status == IssuedBook.STATUS_ISSUED,
        )
        .count()
    )

    total_returned_books = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.status == IssuedBook.STATUS_RETURNED,
        )
        .count()
    )

    pending_requests = (
        db.query(BookRequest)
        .filter(
            BookRequest.status == "pending",
        )
        .count()
    )

    available_books = db.query(func.sum(Book.available_quantity)).scalar() or 0

    return render_template(
        request,
        "admin/dashboard.html",
        user=current_admin,
        total_books=total_books,
        total_users=total_users,
        total_categories=total_categories,
        total_issued_books=total_issued_books,
        total_returned_books=total_returned_books,
        pending_requests=pending_requests,
        available_books=available_books,
        **get_admin_context(db, current_admin),
    )
