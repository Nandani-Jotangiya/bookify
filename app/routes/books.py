from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Book import Book
from app.models.Category import Category

router = APIRouter()

templates = Jinja2Templates(directory="templates")


# ======================================================
# LIST BOOKS
# ======================================================


@router.get("/books")
def list_books(request: Request, db: Session = Depends(get_db)):
    books = db.query(Book).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/books.html",
        context={"request": request, "books": books},
    )


# ======================================================
# ADD BOOK PAGE
# ======================================================


@router.get("/books/add")
def add_book_page(request: Request, db: Session = Depends(get_db)):
    categories = db.query(Category).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/add_books.html",
        context={"request": request, "categories": categories},
    )


# ======================================================
# EDIT BOOK PAGE
# ======================================================


@router.get("/books/edit/{id}")
def edit_book_page(id: int, request: Request, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()

    if not book:
        return RedirectResponse(url="/books", status_code=303)

    categories = db.query(Category).all()

    return templates.TemplateResponse(
        request=request,
        name="admin/edit_book.html",
        context={"request": request, "book": book, "categories": categories},
    )


# ======================================================
# UPDATE BOOK
# ======================================================


@router.post("/books/edit/{id}")
def update_book(
    id: int,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(None),
    rent_per_day: int = Form(...),
    category_id: int = Form(...),
    db: Session = Depends(get_db),
):
    book = db.query(Book).filter(Book.id == id).first()

    if not book:
        return RedirectResponse(url="/books", status_code=303)

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

    if rent_per_day <= 0:
        return {"message": "Rent per day must be greater than 0"}

    if description:
        description = description.strip()

    existing_book = db.query(Book).filter(Book.isbn == isbn, Book.id != id).first()

    if existing_book:
        return {"message": "Book with this ISBN already exists"}

    # Number of books currently issued
    issued_books = book.quantity - book.available_quantity

    # Prevent reducing quantity below issued books
    if quantity < issued_books:
        return {
            "message": f"Cannot reduce quantity below {issued_books}. Books are currently issued."
        }

    # Adjust available quantity
    difference = quantity - book.quantity

    book.title = title
    book.author = author
    book.isbn = isbn
    book.price = price
    book.quantity = quantity
    book.available_quantity += difference
    book.description = description
    book.category_id = category_id
    book.rent_per_day = rent_per_day

    db.commit()

    return RedirectResponse(url="/books", status_code=303)


# ======================================================
# DELETE BOOK
# ======================================================


@router.get("/books/delete/{id}")
def delete_book(id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()

    if book:
        # Prevent deleting a book that is currently issued
        issued_books = book.quantity - book.available_quantity

        if issued_books > 0:
            return {
                "message": "Cannot delete this book because copies are currently issued."
            }

        db.delete(book)
        db.commit()

    return RedirectResponse(url="/books", status_code=303)


# ======================================================
# SAVE BOOK
# ======================================================


@router.post("/books/add")
def save_book(
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    rent_per_day: int = Form(...),
    db: Session = Depends(get_db),
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

    if rent_per_day <= 0:
        return {"message": "Rent per day must be greater than 0"}

    if description:
        description = description.strip()

    existing_book = db.query(Book).filter(Book.isbn == isbn).first()

    if existing_book:
        return {"message": "Book with this ISBN already exists"}

    book = Book(
        title=title,
        author=author,
        isbn=isbn,
        price=price,
        quantity=quantity,
        available_quantity=quantity,
        description=description,
        category_id=category_id,
        rent_per_day=rent_per_day,
    )

    db.add(book)
    db.commit()
    db.refresh(book)

    return RedirectResponse(url="/books", status_code=303)


# ======================================================
# VIEW BOOK
# ======================================================


@router.get("/books/view/{id}")
def view_book(id: int, request: Request, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == id).first()

    if not book:
        return RedirectResponse(url="/books", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="admin/view_book.html",
        context={"request": request, "book": book},
    )
