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
def issued_books(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    if current_user["role"] != "admin":
        return RedirectResponse(url="/login", status_code=303)

    issued_book_records = (
        db.query(IssuedBook, Book, User)
        .join(Book, Book.id == IssuedBook.book_id)
        .join(User, User.id == IssuedBook.user_id)
        .filter(IssuedBook.status == IssuedBook.STATUS_ISSUED)
        .all()
    )

    today = datetime.now(timezone.utc)

    issued_books_data = []

    for issue, book, user in issued_book_records:
        due_date = issue.due_date

        if due_date and due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        late_days = 0

        if due_date and today > due_date:
            late_days = (today - due_date).days

        fine = late_days * 10

        issued_books_data.append(
            {
                "issue": issue,
                "book": book,
                "user": user,
                "late_days": late_days,
                "fine": fine,
                "is_overdue": late_days > 0,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="admin/issued_books.html",
        context={
            "request": request,
            "user": current_user,
            "issued_books": issued_books_data,
        },
    )
