from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.User import User

from app.database import get_db
from app.core.dependencies import get_current_user
from app.models.ChatRequest import ChatRequest

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/user/chat")
def user_chat(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    chat_request = (
        db.query(ChatRequest)
        .filter(ChatRequest.user_id == current_user["user_id"])
        .order_by(ChatRequest.requested_at.desc())
        .first()
    )

    return templates.TemplateResponse(
        request=request,
        name="user/chat.html",
        context={
            "request": request,
            "user": current_user,
            "chat_request": chat_request,
        },
    )


@router.post("/user/chat/request")
def request_chat(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    existing_request = (
        db.query(ChatRequest)
        .filter(
            ChatRequest.user_id == current_user["user_id"],
            ChatRequest.status.in_(["pending", "approved"]),
        )
        .first()
    )

    if existing_request:
        return RedirectResponse(
            url="/user/chat",
            status_code=303,
        )

    new_request = ChatRequest(
        user_id=current_user["user_id"],
        status="pending",
    )

    db.add(new_request)
    db.commit()

    return RedirectResponse(
        url="/user/chat",
        status_code=303,
    )

