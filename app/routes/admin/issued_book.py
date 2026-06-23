from fastapi import APIRouter,Depends,Request
from app.database import get_db
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.auth_dependencies import get_current_user

from app.models.IssuedBook import IssuedBook
from app.models.User import User
from app.models.Book import Book



router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/issued-books")
def issued_books(
    request:Request,
    db:Session = Depends(get_db)
):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )
    issued_books = (
        db.query(
            IssuedBook, 
            User,
            Book
        )
        .join(
            User,
            User.id == IssuedBook.user_id
        )
        .join(
            Book,
            Book.id == IssuedBook.book_id
        )
        .all()
    )
    
    return templates.TemplateResponse(
        "admin/issued_books.html",
        {
        "request":request,
        "user":current_user,
        "issued_books":issued_books
        }
    )