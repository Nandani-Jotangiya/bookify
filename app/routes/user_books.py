from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Book import Book
from app.models.BookRequest import BookRequest
from app.models.IssuedBook import IssuedBook
from app.auth_dependencies import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# USER BOOK LIST
@router.get("/books")
def user_books(request: Request, db: Session = Depends(get_db)):
    books = db.query(Book).all()

    return templates.TemplateResponse(
        "user/books.html", {"request": request, "books": books}
    )


# REQUEST BOOK
@router.post("/user/request-book/{book_id}")
def request_book(
    request: Request,
    book_id: int,
    rental_days: int = Form(...),
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    user_id = current_user["user_id"]

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        return RedirectResponse("/user/books", status_code=303)

    if book.available_quantity <= 0:
        return RedirectResponse("/user/books", status_code=303)

    active_issue = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.user_id == user_id,
            IssuedBook.book_id == book_id,
            IssuedBook.status == "issued",
        )
        .first()
    )

    if active_issue:
        return RedirectResponse("/user/books", status_code=303)

    pending_request = (
        db.query(BookRequest)
        .filter(
            BookRequest.user_id == user_id,
            BookRequest.book_id == book_id,
            BookRequest.status == "pending",
        )
        .first()
    )

    if pending_request:
        return RedirectResponse("/user/books", status_code=303)

    if rental_days <= 0:
        return RedirectResponse("/user/request-book/" + str(book_id), status_code=303)

    total_rent = rental_days * book.rent_per_day

    deposit = total_rent * 0.25

    new_request = BookRequest(
        user_id=user_id, book_id=book_id, rental_days=rental_days, status="pending"
    )

    db.add(new_request)
    db.commit()

    print("Book:", book.title)
    print("Rental Days:", rental_days)
    print("Total Rent:", total_rent)
    print("Deposit:", deposit)

    return RedirectResponse("/user/my-requests", status_code=303)
