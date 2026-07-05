from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.csrf import verify_csrf_or_redirect
from app.core.dependencies import get_logged_in_user
from app.core.templates import render_template
from app.database import get_db
from app.models.Book import Book
from app.models.IssuedBook import IssuedBook


def is_deposit_paid(issue: IssuedBook) -> bool:
    return bool(issue.deposit_paid)


router = APIRouter()


@router.get("/user/payment/{issue_id}")
def payment_page(request: Request, issue_id: int, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    record = (
        db.query(IssuedBook, Book)
        .join(Book, Book.id == IssuedBook.book_id)
        .filter(
            IssuedBook.id == issue_id,
            IssuedBook.user_id == current_user["user_id"],
        )
        .first()
    )

    if not record:
        return RedirectResponse(url="/user/my-requests", status_code=303)

    issue, book = record

    if is_deposit_paid(issue):
        return RedirectResponse(url=f"/user/receipt/{issue_id}", status_code=303)

    return render_template(
        request,
        "user/payment.html",
        user=current_user,
        issue=issue,
        book=book,
    )


@router.post("/user/payment/{issue_id}")
def process_payment(
    request: Request,
    issue_id: int,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    issue = (
        db.query(IssuedBook)
        .filter(
            IssuedBook.id == issue_id,
            IssuedBook.user_id == current_user["user_id"],
        )
        .first()
    )

    if not issue:
        return RedirectResponse(url="/user/my-requests", status_code=303)

    if is_deposit_paid(issue):
        return RedirectResponse(url=f"/user/receipt/{issue_id}", status_code=303)

    issue.deposit_paid = True
    db.commit()

    return RedirectResponse(url=f"/user/receipt/{issue_id}", status_code=303)


@router.get("/user/receipt/{issue_id}")
def receipt_page(request: Request, issue_id: int, db: Session = Depends(get_db)):
    current_user = get_logged_in_user(request)

    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    record = (
        db.query(IssuedBook, Book)
        .join(Book, Book.id == IssuedBook.book_id)
        .filter(
            IssuedBook.id == issue_id,
            IssuedBook.user_id == current_user["user_id"],
        )
        .first()
    )

    if not record:
        return RedirectResponse(url="/user/my-requests", status_code=303)

    issue, book = record

    if not is_deposit_paid(issue):
        return RedirectResponse(url=f"/user/payment/{issue_id}", status_code=303)

    return render_template(
        request,
        "user/receipt.html",
        user=current_user,
        issue=issue,
        book=book,
    )
