from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Book import Book
from app.models.Category import Category

router = APIRouter()

templates = Jinja2Templates(directory="templates")



# LIST BOOKS
@router.get("/books")
def list_books(
    request: Request,
    db: Session = Depends(get_db)
):
    books = db.query(Book).all()

    return templates.TemplateResponse(
        "admin/books.html",
        {
            "request": request,
            "books": books
        }
    )



# ADD BOOK PAGE
@router.get("/books/add")
def add_book_page(
    request: Request,
    db: Session = Depends(get_db)
):
    categories = db.query(Category).all()

    return templates.TemplateResponse(
        "admin/add_books.html",
        {
            "request": request,
            "categories": categories
        }
    )
# EDIT BOOK
@router.get("/books/edit/{id}")
def edit_book_page(id:int,request:Request,db:Session = Depends(get_db)):
    
    book = db.query(Book).filter(Book.id == id).first()

    if not book:
        return RedirectResponse(
        url="/books",
        status_code=303
    )

    categories = db.query(Category).all()

    return templates.TemplateResponse(
        "admin/edit_book.html",{
            "request":request,
            "book":book,
            "categories":categories
        }
    )

#UPDATE BOOK
@router .post("/books/edit/{id}")
def update_book(
    id:int,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    db: Session = Depends(get_db)   
):
    book = db.query(Book).filter(Book.id == id).first()

    if not book:
        return RedirectResponse(
            url="/books",
            status_code=303 
        )
    
    title = title.strip()
    author = author.strip()
    isbn = isbn.strip()

    if not title:
        return {"message": "Title is required"}

    if not author:
        return {"message": "Author is required"}

    if not isbn:
        return {"message": "ISBN is required"}

    if price <= 0:
        return {"message": "Price must be greater than 0"}

    if quantity <= 0:
        return {"message": "Quantity must be greater than 0"}
    
    if description:
        description = description.strip()
    
    existing_book = (
        db.query(Book)
        .filter(Book.isbn == isbn,
                Book.id != id)
        .first()
    )

    if existing_book:
        return {
            "message": "Book with this ISBN already exists"
        }

   
    book.title = title
    book.author = author
    book.isbn = isbn
    book.price = price
    book.quantity = quantity
    book.description = description
    book.category_id = category_id
    
    db.commit()

    return RedirectResponse(
        url="/books",
        status_code=303
    )


#DELETE BOOK

@router.get("/books/delete/{id}")
def delete_book(
    id:int,
    db:Session = Depends(get_db)
):
    book  = db.query(Book).filter(Book.id == id).first()

    if book:
        db.delete(book)
        db.commit()

    return  RedirectResponse(
        url="/books",
        status_code=303
    )

# SAVE BOOK
@router.post("/books/add")
def save_book(
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    db: Session = Depends(get_db)
):
    title = title.strip()
    author = author.strip()
    isbn = isbn.strip()

    if not title:
        return {"message": "Title is required"}

    if not author:
        return {"message": "Author is required"}

    if not isbn:
        return {"message": "ISBN is required"}

    if price <= 0:
        return {"message": "Price must be greater than 0"}

    if quantity <= 0:
        return {"message": "Quantity must be greater than 0"}

    existing_book = (
        db.query(Book)
        .filter(Book.isbn == isbn)
        .first()
    )

    if existing_book:
        return {
            "message": "Book with this ISBN already exists"
        }

    book = Book(
        title=title,
        author=author,
        isbn=isbn,
        price=price,
        quantity=quantity,
        description=description,
        category_id=category_id
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return RedirectResponse(
        url="/books",
        status_code=303
    )

@router.get("/books/view/{id}")
def view_book(
    id:int,
    request:Request,
    db:Session = Depends(get_db)
):
    
    book = db.query(Book).filter(Book.id == id).first()

    if not book :
        return RedirectResponse(
            url="/books",
            status_code=303
        )
    
    return  templates.TemplateResponse (
        "admin/view_book.html",
        {
            "request":request,
            "book":book
        }
    )