from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.csrf import verify_csrf_or_redirect
from app.core.dependencies import get_admin_user
from app.core.context import unread_admin_notification_count
from app.core.templates import render_template
from app.database import get_db
from app.models.Book import Book
from app.models.BookRequest import BookRequest
from app.models.IssuedBook import IssuedBook
from app.models.User import User
from app.services.fine import calculate_fine

from app.services.notification_service import create_notification
from app.enums.notification_type import NotificationType

router = APIRouter()


def _load_admin_requests(db: Session):
    return (
        db.query(BookRequest, Book, User)
        .join(Book, Book.id == BookRequest.book_id)
        .join(User, User.id == BookRequest.user_id)
        .order_by(BookRequest.id.desc())
        .all()
    )


@router.get("/admin/requests")
def admin_requests(
    request: Request,
    error: str | None = None,
    db: Session = Depends(get_db),
):
    current_admin = get_admin_user(request)

    if not current_admin:
        return RedirectResponse(url="/login", status_code=303)

    notification_count = unread_admin_notification_count(
        db,
        current_admin["user_id"],
    )

    return render_template(
        request,
        "admin/requests.html",
        requests=_load_admin_requests(db),
        error=error,
        unread_admin_notification_count=notification_count,
    )


@router.post("/admin/request/{request_id}/approve")
def approve_request(
    request: Request,
    request_id: int,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse("/login", status_code=303)

    book_request = db.query(BookRequest).filter(BookRequest.id == request_id).first()

    if not book_request:
        notification_count = unread_admin_notification_count(
            db,
            get_admin_user(request)["user_id"],
        )

        return render_template(
            request,
            "admin/requests.html",
            requests=_load_admin_requests(db),
            error="Request not found.",
            unread_admin_notification_count=notification_count,
        )

    if book_request.status != "pending":
        return RedirectResponse(url="/admin/requests", status_code=303)

    book = book_request.book

    if book.available_quantity <= 0:
        notification_count = unread_admin_notification_count(
            db,
            get_admin_user(request)["user_id"],
        )

        return render_template(
            request,
            "admin/requests.html",
            requests=_load_admin_requests(db),
            error="Book is not available.",
            unread_admin_notification_count=notification_count,
        )

    book_request.status = "approved"
    book.available_quantity -= 1

    now_utc = datetime.now(UTC)

    rent = book_request.rental_days * book.rent_per_day
    deposit = rent * 0.25

    issued_book = IssuedBook(
        user_id=book_request.user_id,
        book_id=book_request.book_id,
        request_id=book_request.id,
        issued_date=now_utc,
        due_date=now_utc + timedelta(days=book_request.rental_days),
        rent_amount=rent,
        deposit_amount=deposit,
        fine_amount=0,
        deposit_paid=False,
        status=IssuedBook.STATUS_ISSUED,
    )

    db.add(issued_book)
    db.commit()

    create_notification(
        db=db,
        user_id=book_request.user_id,
        title="Request Approved",
        message=f'Your request for "{book.title}" has been approved.',
        notification_type=NotificationType.REQUEST_APPROVED,
    )

    create_notification(
        db=db,
        user_id=book_request.user_id,
        title="Book Issued",
        message=f'"{book.title}" has been issued to you.',
        notification_type=NotificationType.BOOK_ISSUED,
    )

    return RedirectResponse(url="/admin/requests", status_code=303)


@router.post("/admin/request/{request_id}/reject")
def reject_request(
    request: Request,
    request_id: int,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse("/login", status_code=303)

    book_request = db.query(BookRequest).filter(BookRequest.id == request_id).first()

    if not book_request:
        notification_count = unread_admin_notification_count(
            db,
            get_admin_user(request)["user_id"],
        )

        return render_template(
            request,
            "admin/requests.html",
            requests=_load_admin_requests(db),
            error="Request not found.",
            unread_admin_notification_count=notification_count,
        )

    book_request.status = "rejected"
    db.commit()

    create_notification(
        db=db,
        user_id=book_request.user_id,
        title="Request Rejected",
        message=f'Your request for "{book_request.book.title}" has been rejected.',
        notification_type=NotificationType.REQUEST_REJECTED,
    )

    return RedirectResponse(url="/admin/requests", status_code=303)


@router.post("/admin/return-book/{issue_id}")
def return_book(
    request: Request,
    issue_id: int,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_redirect = verify_csrf_or_redirect(request, csrf_token)
    if csrf_redirect:
        return csrf_redirect

    if not get_admin_user(request):
        return RedirectResponse(url="/login", status_code=303)

    issued_book = db.query(IssuedBook).filter(IssuedBook.id == issue_id).first()

    if not issued_book:
        return RedirectResponse(
            url="/admin/issued-books?error=Issued+book+not+found",
            status_code=303,
        )

    if issued_book.status == IssuedBook.STATUS_RETURNED:
        return RedirectResponse(url="/admin/issued-books", status_code=303)

    return_date = datetime.now(UTC)

    late_days, fine_amount = calculate_fine(issued_book.due_date, return_date)

    issued_book.return_date = return_date
    issued_book.status = IssuedBook.STATUS_RETURNED
    issued_book.late_days = late_days
    issued_book.fine_amount = fine_amount

    book = db.query(Book).filter(Book.id == issued_book.book_id).first()

    if book:
        book.available_quantity += 1

    db.commit()

    create_notification(
        db=db,
        user_id=issued_book.user_id,
        title="Book Returned",
        message=f'Thank you for returning "{book.title}".',
        notification_type=NotificationType.BOOK_RETURNED,
    )

    return RedirectResponse(url="/admin/issued-books", status_code=303)
