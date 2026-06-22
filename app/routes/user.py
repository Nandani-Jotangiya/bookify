from fastapi import APIRouter, Request,Depends
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.models.IssuedBook import IssuedBook
from app.models.Book import Book
from app.models.BookRequest import BookRequest
from app.database import get_db
from app.auth_dependencies import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/user/dashboard")
def user_dashboard(request: Request):

    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if current_user["role"] != "user":
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        "user/dashboard.html",
        {
            "request": request,
            "user": current_user
        }
    )

@router.get("/user/books")
def user_books(request:Request,db:Session = Depends(get_db)):

    current_user = get_current_user(request)

    if not current_user :
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    
    books = db.query(Book).all()

    return templates.TemplateResponse(
        "user/books.html",
        {
            "request":request,
            "user":current_user,
            "books":books
        }
    )
    
@router.get("/user/history")
def user_history(request:Request,db:Session = Depends(get_db)):

    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    
    return templates.TemplateResponse(
        "user/history.html",
        {
            "request":request,
            "user":current_user,
        
        }
    )

@router.post("/user/request-book/{book_id}")
def request_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    # Check JWT authentication
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    user_id = current_user["user_id"]

    # Check if book exists
    book = db.query(Book).filter(
        Book.id == book_id
    ).first()

    if not book:
        return RedirectResponse(
            url="/user/books",
            status_code=303
        )

    # Prevent duplicate requests
    existing_request = (
        db.query(BookRequest)
        .filter(
            BookRequest.user_id == user_id,
            BookRequest.book_id == book_id
        )
        .first()
    )

    if existing_request:
        return RedirectResponse(
            url="/user/books",
            status_code=303
        )

    # Create new request
    new_request = BookRequest(
        user_id=user_id,
        book_id=book_id,
        status="pending"
    )

    db.add(new_request)
    db.commit()

    return RedirectResponse(
        url="/user/books",
        status_code=303
    )

@router.get("/user/my-requests")
def my_requests(request:Request,db:Session = Depends(get_db)):

    current_user = get_current_user(request)

    if not current_user :
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    
    requests = (
        db.query(
        BookRequest,
        Book
     )
     .join(
        Book,
        Book.id == BookRequest.book_id
     )
     .filter(
        BookRequest.user_id == current_user["user_id"]
        )
     .all()
    )

    
    return templates.TemplateResponse(
        "user/my_requests.html",
        {
            "request" : request,
            "requests" : requests
        }
    )

@router.get("/user/issued-books")
def issued_books_page(
    request: Request,
    db: Session = Depends(get_db)
):

    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    issued_books = (
    db.query(IssuedBook, Book)
    .join(Book, Book.id == IssuedBook.book_id)
    .filter(
        IssuedBook.user_id == current_user["user_id"]
    )
    .all()
)
    print("ISSUED BOOKS =", issued_books)

    return templates.TemplateResponse(
        "user/issued_books.html",
        {
            "request": request,
            "user": current_user,
            "issued_books": issued_books
        }
    )