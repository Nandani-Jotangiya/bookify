from fastapi import APIRouter, Request, Depends
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
def user_books(
    request: Request,
    db: Session = Depends(get_db)
):
    books = db.query(Book).all()

    return templates.TemplateResponse(
        "user/books.html",
        {
            "request": request,
            "books": books
        }
    )


# REQUEST BOOK
@router.post("/user/request-book/{book_id}")
def request_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Check book exists
    book = (
        db.query(Book)
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        return RedirectResponse(
            url="/books",
            status_code=303
        )

    # Check stock available
    if book.available_quantity <= 0:
        return RedirectResponse(
            url="/books",
            status_code=303
        )

    # Check if user already has this book issued
    active_issue = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.user_id == current_user["user_id"],
            IssuedBook.book_id == book_id,
            IssuedBook.status == "issued"
        )
        .first()
    )

    if active_issue:
        return RedirectResponse(
            url="/books",
            status_code=303
        )

    # Check pending request
    pending_request = (
        db.query(BookRequest)
        .filter(
            BookRequest.user_id == current_user["user_id"],
            BookRequest.book_id == book_id,
            BookRequest.status == "pending"
        )
        .first()
    )

    if pending_request:
        return RedirectResponse(
            url="/books",
            status_code=303
        )

    # Create request
    new_request = BookRequest(
        user_id=current_user["user_id"],
        book_id=book_id,
        status="pending"
    )

    db.add(new_request)
    db.commit()

    print("REQUEST CREATED")
    print("USER ID =", current_user["user_id"])
    print("BOOK ID =", book_id)

    return RedirectResponse(
        url="/books",
        status_code=303
    )