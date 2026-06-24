from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.database import get_db
from app.auth_dependencies import get_current_user

from app.models.IssuedBook import IssuedBook
from app.models.User import User
from app.models.Book import Book

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin/issued-books")
def issued_books(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    issued_book_records = (
        db.query(
            IssuedBook,
            User,
            Book
        )
        .join(
            User,
            User.id == IssuedBook.user_id
        )
        .join(
            Book,
            Book.id == IssuedBook.book_id
        )
        .all()
    )

    return templates.TemplateResponse(
        "admin/issued_books.html",
        {
            "request": request,
            "user": current_user,
            "issued_books": issued_book_records
        }
    )


@router.get("/admin/return-book/{issue_id}")
def return_book(
    issue_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    issue = (
        db.query(IssuedBook)
        .filter(IssuedBook.id == issue_id)
        .first()
    )

    if not issue:
        return RedirectResponse(
            url="/admin/issued-books",
            status_code=303
        )

    # Prevent double return
    if issue.status == "returned":
        return RedirectResponse(
            url="/admin/issued-books",
            status_code=303
        )

    book = (
        db.query(Book)
        .filter(Book.id == issue.book_id)
        .first()
    )

    # Mark issue as returned
    issue.status = "returned"
    issue.return_date = datetime.now(timezone.utc)

    # Restore book quantity
    # Replace available_quantity with your actual field if different
    book.available_quantity += 1

    db.commit()

    return RedirectResponse(
        url="/admin/issued-books",
        status_code=303
    )