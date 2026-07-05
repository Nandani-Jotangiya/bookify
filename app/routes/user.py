from datetime import datetime, timezone

from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from app.core.csrf import verify_csrf_or_redirect
from app.core.dependencies import get_logged_in_user
from app.core.templates import render_template
from app.models.IssuedBook import IssuedBook
from app.models.Book import Book
from app.models.BookRequest import BookRequest
from app.database import get_db

router = APIRouter()


@router.get("/user/dashboard")
def user_dashboard(request: Request, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_id = current_user["user_id"]

    total_books = db.query(Book).filter(Book.available_quantity > 0).count()
    total_requests = (
        db.query(BookRequest).filter(BookRequest.user_id == user_id).count()
    )
    total_issued = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.user_id == user_id,
            IssuedBook.status == IssuedBook.STATUS_ISSUED,
        )
        .count()
    )
    total_returned = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.user_id == user_id,
            IssuedBook.status == IssuedBook.STATUS_RETURNED,
        )
        .count()
    )

    return render_template(
        request,
        "user/dashboard.html",
        user=current_user,
        total_books=total_books,
        total_requests=total_requests,
        total_issued=total_issued,
        total_returned=total_returned,
    )


@router.get("/user/books")
def user_books(request: Request, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    books = db.query(Book).all()

    return render_template(request, "user/books.html", user=current_user, books=books)


@router.get("/user/history")
def user_history(request: Request, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_id = current_user["user_id"]

    returned_books = (
        db.query(IssuedBook, Book)
        .join(Book, Book.id == IssuedBook.book_id)
        .filter(
            IssuedBook.user_id == user_id,
            IssuedBook.status == IssuedBook.STATUS_RETURNED,
        )
        .order_by(IssuedBook.return_date.desc())
        .all()
    )

    past_requests = (
        db.query(BookRequest, Book)
        .join(Book, Book.id == BookRequest.book_id)
        .filter(BookRequest.user_id == user_id)
        .order_by(BookRequest.id.desc())
        .all()
    )

    return render_template(
        request,
        "user/history.html",
        user=current_user,
        returned_books=returned_books,
        past_requests=past_requests,
    )


@router.get("/user/my-requests")
def my_requests(request: Request, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    requests = (
        db.query(BookRequest, Book, IssuedBook)
        .join(Book, Book.id == BookRequest.book_id)
        .outerjoin(IssuedBook, IssuedBook.request_id == BookRequest.id)
        .filter(BookRequest.user_id == current_user["user_id"])
        .order_by(BookRequest.id.desc())
        .all()
    )

    return render_template(request, "user/my_requests.html", requests=requests)


@router.get("/user/issued-books")
def issued_books_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    today = datetime.now(timezone.utc)

    records = (
        db.query(IssuedBook, Book)
        .join(Book, Book.id == IssuedBook.book_id)
        .filter(
            IssuedBook.user_id == current_user["user_id"],
            IssuedBook.status == IssuedBook.STATUS_ISSUED,
        )
        .order_by(IssuedBook.due_date.asc())
        .all()
    )

    issued_books = []

    for issue, book in records:
        due_date = issue.due_date
        if due_date and due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        is_overdue = bool(due_date and today > due_date)
        deposit_paid = bool(issue.deposit_paid)

        issued_books.append(
            {
                "issue": issue,
                "book": book,
                "is_overdue": is_overdue,
                "deposit_paid": deposit_paid,
            }
        )

    return render_template(
        request,
        "user/issued_books.html",
        user=current_user,
        issued_books=issued_books,
    )


@router.get("/user/request-book/{book_id}")
def request_book_page(book_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        return RedirectResponse("/user/books", status_code=303)

    return render_template(
        request, "user/request_book.html", user=current_user, book=book
    )


@router.post("/user/request-book/{book_id}")
def request_book(
    request: Request,
    book_id: int,
    rental_days: int = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        return RedirectResponse("/user/books", status_code=303)

    if book.available_quantity <= 0:
        return RedirectResponse("/user/books", status_code=303)

    existing_request = (
        db.query(BookRequest)
        .filter(
            BookRequest.user_id == current_user["user_id"],
            BookRequest.book_id == book_id,
            BookRequest.status == "pending",
        )
        .first()
    )

    if existing_request:
        return RedirectResponse("/user/my-requests", status_code=303)

    new_request = BookRequest(
        user_id=current_user["user_id"],
        book_id=book_id,
        rental_days=rental_days,
        status="pending",
    )

    db.add(new_request)
    db.commit()

    return RedirectResponse("/user/my-requests", status_code=303)
