from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_admin_user
from app.core.templates import render_template
from app.database import get_db
from app.models.Book import Book
from app.models.IssuedBook import IssuedBook
from app.models.User import User

router = APIRouter()


@router.get("/admin/history")
def admin_history(request: Request, db: Session = Depends(get_db)):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    history_records = (
        db.query(IssuedBook, Book, User)
        .join(Book, Book.id == IssuedBook.book_id)
        .join(User, User.id == IssuedBook.user_id)
        .filter(IssuedBook.status == IssuedBook.STATUS_RETURNED)
        .order_by(IssuedBook.return_date.desc())
        .all()
    )

    return render_template(
        request, "admin/history.html", history_records=history_records
    )
