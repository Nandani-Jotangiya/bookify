from fastapi import APIRouter,Request,Form,Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import session

from app.database import get_db
from app.models.Book import Book
from app.models.Category import Category

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ADD BOOK PAGE
@router.get("/books/add")
def add_book_page(request:Request,db:session = Depends(get_db)):

    categories = db.query(Category).all()

    return templates.TemplateResponse(
        "admin/add_books.html",
        {
            "request":request,
            "categories":categories
        }
    )

# SAVE BOOK

@router.post("/books/add")
def save_book(
    title:str = Form(...),
    author:str = Form(...),
    price:float = Form(...),
    description:str = Form(None),
    category_id:int = Form(...),
    db:session = Depends(get_db)
):
    book = Book(
        title=title,
        author = author,
        price = price,
        description = description,
        category_id = category_id
    )

    db.add(book)
    db.commit()

    return RedirectResponse(url="/books",status_code=303)

@router.get("/books")
def list_books(request:Request,db:session= Depends(get_db)):

    books = db.query(Book).all()

    return templates.TemplateResponse(
        "admin/books.html", {
            "request":request,
            "books":books
        }   
    )

@router.get("/books/add")
def add_book_page(request:Request,db:session = Depends(get_db)):

    categories = db.query(Category).all()

    return templates.TemplateResponse(
        "admin/add_books.html",
        {
            "request":request,
            "categories" :categories
        }
    )
