from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.BookRequest import BookRequest
from app.models.Book import Book
from app.models.User import User
from app.auth_dependencies import get_current_user
from app.utils.fine import calculate_fine

from app.models.IssuedBook import IssuedBook
from datetime import datetime, timedelta, UTC

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/admin/requests")
def admin_requests(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    if current_user["role"] != "admin":
        return RedirectResponse(url="/login", status_code=303)

    requests = (
        db.query(BookRequest, Book, User)
        .join(Book, Book.id == BookRequest.book_id)
        .join(User, User.id == BookRequest.user_id)
        .order_by(BookRequest.id.desc())
        .all()
    )

    # FIXED: Added explicit keyword arguments to match modern FastAPI syntax
    return templates.TemplateResponse(
        request=request,
        name="admin/requests.html",
        context={"request": request, "requests": requests},
    )


@router.get("/admin/request/{request_id}/approve")
def approve_request(request: Request, request_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    if current_user["role"] != "admin":
        return RedirectResponse("/login", status_code=303)

    book_request = db.query(BookRequest).filter(BookRequest.id == request_id).first()

    if not book_request:
        return {"error": "request not found"}

    if book_request.status != "pending":
        return RedirectResponse(url="/admin/requests", status_code=303)

    book = book_request.book

    if book.available_quantity <= 0:
        return {"error": "Book not available"}

    book_request.status = "approved"
    book.available_quantity -= 1

    # Using naive datetimes if your DB schema is naive,
    # or explicit UTC if your columns store timezone data.
    now_utc = datetime.now(UTC)

    rent = book_request.rental_days * book.rent_per_day
    deposit = rent * 0.25

    issued_book = IssuedBook(
        user_id=book_request.user_id,
        book_id=book_request.book_id,
        request_id=book_request.id,
        issued_date=now_utc,
        due_date=now_utc + timedelta(days=book_request.rental_days),
        rent_amount=rent,
        deposit_amount=deposit,
        fine_amount=0,
        status=IssuedBook.STATUS_ISSUED,
    )

    db.add(issued_book)
    db.commit()

    return RedirectResponse(url="/admin/requests", status_code=303)


@router.get("/admin/request/{request_id}/reject")
def reject_request(request: Request, request_id: int, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    if current_user["role"] != "admin":
        return RedirectResponse("/login", status_code=303)

    book_request = db.query(BookRequest).filter(BookRequest.id == request_id).first()

    if not book_request:
        return {"error": "request not found"}

    book_request.status = "rejected"
    db.commit()

    return RedirectResponse(url="/admin/requests", status_code=303)


@router.get("/admin/return-book/{issue_id}")
def return_book(issue_id: int, db: Session = Depends(get_db)):
    issued_book = db.query(IssuedBook).filter(IssuedBook.id == issue_id).first()

    if not issued_book:
        return {"error": "Issued book not found"}

    if issued_book.status == IssuedBook.STATUS_RETURNED:
        return RedirectResponse(url="/admin/issued-books", status_code=303)

    # Return time
    return_date = datetime.now(UTC)

    # Calculate fine
    late_days, fine_amount = calculate_fine(issued_book.due_date, return_date)

    # Update issued book
    issued_book.return_date = return_date
    issued_book.status = IssuedBook.STATUS_RETURNED
    issued_book.late_days = late_days
    issued_book.fine_amount = fine_amount

    # Increase available quantity
    book = db.query(Book).filter(Book.id == issued_book.book_id).first()

    if book:
        book.available_quantity += 1

    db.commit()

    return RedirectResponse(url="/admin/issued-books", status_code=303)
