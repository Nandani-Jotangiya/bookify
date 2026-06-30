from fastapi import APIRouter, Request, Depends, Form
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.IssuedBook import IssuedBook
from app.models.Book import Book
from app.models.User import User
from app.models.BookRequest import BookRequest
from app.database import get_db
from app.auth_dependencies import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/user/dashboard")
def user_dashboard(request: Request):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="user/dashboard.html",
        context={"request": request, "user": current_user},
    )


@router.get("/user/books")
def user_books(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    books = db.query(Book).all()

    return templates.TemplateResponse(
        request=request,
        name="user/books.html",
        context={"request": request, "user": current_user, "books": books},
    )


@router.get("/user/history")
def user_history(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="user/history.html",
        context={
            "request": request,
            "user": current_user,
        },
    )


@router.get("/user/my-requests")
def my_requests(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    requests = (
        db.query(BookRequest, Book)
        .join(Book, Book.id == BookRequest.book_id)
        .filter(BookRequest.user_id == current_user["user_id"])
        .all()
    )

    # Fixed syntax error below
    return templates.TemplateResponse(
        request=request,
        name="user/my_requests.html",
        context={"request": request, "requests": requests},
    )


@router.get("/user/issued-books")
def issued_books_page(request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    issued_books = (
        db.query(IssuedBook, Book)
        .join(Book, Book.id == IssuedBook.book_id)
        .filter(IssuedBook.user_id == current_user["user_id"])
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="user/issued_books.html",
        context={
            "request": request,
            "user": current_user,
            "issued_books": issued_books,
        },
    )


@router.get("/user/request-book/{book_id}")
def request_book_page(book_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        return RedirectResponse("/user/books", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="user/request_book.html",
        context={"request": request, "user": current_user, "book": book},
    )


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
