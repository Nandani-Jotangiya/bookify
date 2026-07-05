from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.csrf import verify_csrf_or_redirect
from app.core.dependencies import get_admin_user
from app.core.templates import render_template
from app.database import get_db
from app.models.Book import Book
from app.models.Category import Category

router = APIRouter()


def _normalize_description(description: str | None) -> str:
    if not description:
        return ""
    return description.strip()


@router.get("/books")
def list_books(request: Request, db: Session = Depends(get_db)):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    books = db.query(Book).all()

    return render_template(request, "admin/books.html", books=books)


@router.get("/books/add")
def add_book_page(request: Request, db: Session = Depends(get_db)):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    categories = db.query(Category).all()

    return render_template(request, "admin/add_books.html", categories=categories)


@router.get("/books/edit/{id}")
def edit_book_page(id: int, request: Request, db: Session = Depends(get_db)):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    book = db.query(Book).filter(Book.id == id).first()

    if not book:
        return RedirectResponse(url="/books", status_code=303)

    categories = db.query(Category).all()

    return render_template(
        request, "admin/edit_book.html", book=book, categories=categories
    )


@router.post("/books/edit/{id}")
def update_book(
    request: Request,
    id: int,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(None),
    rent_per_day: int = Form(...),
    category_id: int = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    book = db.query(Book).filter(Book.id == id).first()
    categories = db.query(Category).all()

    if not book:
        return RedirectResponse(url="/books", status_code=303)

    title = title.strip()
    author = author.strip()
    isbn = isbn.strip()
    description = _normalize_description(description)

    if not title:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error="Title is required",
        )

    if not author:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error="Author is required",
        )

    if not isbn:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error="ISBN is required",
        )

    if price <= 0:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error="Price must be greater than 0",
        )

    if quantity <= 0:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error="Quantity must be greater than 0",
        )

    if rent_per_day <= 0:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error="Rent per day must be greater than 0",
        )

    existing_book = db.query(Book).filter(Book.isbn == isbn, Book.id != id).first()

    if existing_book:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error="Book with this ISBN already exists",
        )

    issued_books = book.quantity - book.available_quantity

    if quantity < issued_books:
        return render_template(
            request,
            "admin/edit_book.html",
            book=book,
            categories=categories,
            error=f"Cannot reduce quantity below {issued_books}. Books are currently issued.",
        )

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


@router.post("/books/delete/{id}")
def delete_book(
    id: int,
    request: Request,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    book = db.query(Book).filter(Book.id == id).first()

    if book:
        issued_books = book.quantity - book.available_quantity

        if issued_books > 0:
            books = db.query(Book).all()
            return render_template(
                request,
                "admin/books.html",
                books=books,
                error="Cannot delete this book because copies are currently issued.",
            )

        db.delete(book)
        db.commit()

    return RedirectResponse(url="/books", status_code=303)


@router.post("/books/add")
def save_book(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    isbn: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    description: str = Form(None),
    category_id: int = Form(...),
    rent_per_day: int = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    categories = db.query(Category).all()
    title = title.strip()
    author = author.strip()
    isbn = isbn.strip()
    description = _normalize_description(description)

    if not title:
        return render_template(
            request,
            "admin/add_books.html",
            categories=categories,
            error="Title is required",
        )

    if not author:
        return render_template(
            request,
            "admin/add_books.html",
            categories=categories,
            error="Author is required",
        )

    if not isbn:
        return render_template(
            request,
            "admin/add_books.html",
            categories=categories,
            error="ISBN is required",
        )

    if price <= 0:
        return render_template(
            request,
            "admin/add_books.html",
            categories=categories,
            error="Price must be greater than 0",
        )

    if quantity <= 0:
        return render_template(
            request,
            "admin/add_books.html",
            categories=categories,
            error="Quantity must be greater than 0",
        )

    if rent_per_day <= 0:
        return render_template(
            request,
            "admin/add_books.html",
            categories=categories,
            error="Rent per day must be greater than 0",
        )

    existing_book = db.query(Book).filter(Book.isbn == isbn).first()

    if existing_book:
        return render_template(
            request,
            "admin/add_books.html",
            categories=categories,
            error="Book with this ISBN already exists",
        )

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


@router.get("/books/view/{id}")
def view_book(id: int, request: Request, db: Session = Depends(get_db)):
    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    book = db.query(Book).filter(Book.id == id).first()

    if not book:
        return RedirectResponse(url="/books", status_code=303)

    return render_template(request, "admin/view_book.html", book=book)
