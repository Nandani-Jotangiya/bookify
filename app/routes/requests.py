from fastapi import APIRouter,Depends,Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.BookRequest import BookRequest
from app.auth_dependencies import get_current_user

from app.models.IssuedBook import IssuedBook
from datetime import datetime, timedelta,UTC

router = APIRouter()

templates = Jinja2Templates(directory="templates")

from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app.database import get_db
from app.models.BookRequest import BookRequest

from app.auth_dependencies import get_current_user

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/admin/requests")
def admin_requests(
    request: Request,
    db: Session = Depends(get_db)
):

    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    if current_user["role"] != "admin":
        return RedirectResponse(
            url="/login",
            status_code=303
        )

    requests = (
        db.query(BookRequest)
        .order_by(BookRequest.id.desc())
        .all()
    )

    return templates.TemplateResponse(
        "admin/requests.html",
        {
            "request": request,
            "requests": requests
        }
    )

@router.get("/admin/request/{request_id}/approve")
def approve_request(
    request_id:int,
    db:Session = Depends(get_db)

):
    book_request = db.query(BookRequest).filter(BookRequest.id == request_id).first()

    if not book_request :
        return {"error":"request not found"}


    book_request.status = "Approved"

    issued_book = IssuedBook(
        user_id=book_request.user_id,
        book_id = book_request.book_id,
        due_date =  datetime.now(UTC) + timedelta(days=14)
    )
    
    db.add(issued_book)

    db.commit()

    return RedirectResponse(
        url="/admin/requests",
        status_code=303
    )


@router.get("/admin/request/{request_id}/reject")
def reject_request (
    request_id:int,
    db:Session = Depends(get_db)
):
    book_request = db.query(BookRequest).filter(BookRequest.id == request_id).first()
     
    if not book_request :
        return {"error":"request not found"}

    book_request.status = "Rejected"

    db.commit()

    return RedirectResponse(
        url="/admin/requests",
        status_code=303
    )