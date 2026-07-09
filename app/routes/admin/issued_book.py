from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.context import get_admin_context
from app.core.dependencies import get_admin_user
from app.core.templates import render_template
from app.database import get_db
from app.models.Book import Book
from app.models.IssuedBook import IssuedBook
from app.models.User import User
from app.services.fine import FINE_PER_DAY

router = APIRouter()


@router.get("/admin/issued-books")
def issued_books(
    request: Request,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    current_admin = get_admin_user(request)

    if not current_admin:
        return RedirectResponse("/login", status_code=303)

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

        fine = late_days * FINE_PER_DAY

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

    return render_template(
        request,
        "admin/issued_books.html",
        issued_books=issued_books_data,
        error=error,
        **get_admin_context(db, current_admin),
    )