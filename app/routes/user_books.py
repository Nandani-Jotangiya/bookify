from fastapi import FastAPI,APIRouter,Request,Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import  Session
from app.models.Book import Book
from app.models.BookRequest import BookRequest
from fastapi.templating import Jinja2Templates

from app.auth_dependencies import get_current_user

from app.database import get_db

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/books")
def user_books(request:Request,db:Session = Depends(get_db)):

    books = db.query(Book).all()

    return templates.TemplateResponse(
        request=request,
        name="user/books.html",
        context={
            "request": request,
            "books": books
        }
    )

@router.post("/user/request-book/{book_id}")
def request_book(
    book_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_current_user(request)

    if not current_user:

        return RedirectResponse (
            url="/login",
            status_code=303
        )

    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        return RedirectResponse (
            url="/books",
            status_code=303
        )
    existing_request = (
        db.query(BookRequest)
        .filter(
        BookRequest.user_id == current_user["user_id"],
        BookRequest.book_id == book_id,
        BookRequest.status == "Pending"
    )
    .first()
)

    if existing_request :
        return RedirectResponse(
            url="/books",
            status_code=303
            )
    
    new_request = BookRequest(
        user_id=current_user["user_id"],
        book_id = book_id,
        status = "Pending"
    )

    db.add(new_request)
    db.commit()
    print("CREATING REQUEST")
    print("USER =", current_user["user_id"])
    print("BOOK =", book_id)

    return RedirectResponse(
        url="/books",
        status_code=303
    )