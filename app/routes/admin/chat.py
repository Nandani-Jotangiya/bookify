from datetime import datetime, UTC

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.templates import render_template
from app.core.context import get_admin_context
from app.models.ChatMessage import ChatMessage

from app.models.ChatRequest import ChatRequest
from app.models.User import User

router = APIRouter()


@router.get("/admin/chat/requests")
def admin_chat_requests(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Allow only admins
    if current_user["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    chat_requests = (
        db.query(ChatRequest)
        .join(User, ChatRequest.user_id == User.id)
        .order_by(ChatRequest.requested_at.desc())
        .all()
    )

    context = get_admin_context(
        db=db,
        current_admin=current_user,
    )

    context.update(
        {
            "requests": chat_requests,
            "user": current_user,
        }
    )

    return render_template(
        request=request,
        name="admin/chat_requests.html",
        **context,
    )


@router.get("/admin/chat/{chat_request_id}")
def admin_chat(
    chat_request_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Only admins can access
    if current_user["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    # Find the approved chat request
    chat_request = (
        db.query(ChatRequest)
        .filter(
            ChatRequest.id == chat_request_id,
            ChatRequest.status == "approved",
        )
        .first()
    )

    if not chat_request:
        return RedirectResponse(
            "/admin/chat/requests",
            status_code=303,
        )

    # Load all messages
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_request_id == chat_request.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    # Admin sidebar context
    context = get_admin_context(
        db=db,
        current_admin=current_user,
    )

    context.update(
        {
            "user": current_user,
            "chat_request": chat_request,
            "messages": messages,
        }
    )

    return render_template(
        request=request,
        name="admin/chat_messages.html",
        **context,
    )


@router.post("/admin/chat/{request_id}/approve")
def approve_chat_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    chat_request = db.query(ChatRequest).filter(ChatRequest.id == request_id).first()

    if not chat_request:
        return RedirectResponse(
            "/admin/chat/requests",
            status_code=303,
        )
    (
        db.query(ChatMessage)
        .filter(
            ChatMessage.chat_request_id == chat_request.id,
            ChatMessage.receiver_id == current_user["user_id"],
            ChatMessage.is_read == False,
        )
        .update(
            {
                ChatMessage.is_read: True,
            }
        )
    )

    if chat_request.status == "approved":
        return RedirectResponse(
            "/admin/chat/requests",
            status_code=303,
        )

    chat_request.status = "approved"
    chat_request.approved_at = datetime.now(UTC)
    chat_request.admin_id = current_user["user_id"]

    db.commit()

    return RedirectResponse(
        "/admin/chat/requests",
        status_code=303,
    )


@router.post("/admin/chat/{request_id}/reject")
def reject_chat_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        return RedirectResponse("/", status_code=303)

    chat_request = db.query(ChatRequest).filter(ChatRequest.id == request_id).first()

    if not chat_request:
        return RedirectResponse(
            "/admin/chat/requests",
            status_code=303,
        )

    if chat_request.status == "rejected":
        return RedirectResponse(
            "/admin/chat/requests",
            status_code=303,
        )

    chat_request.status = "rejected"
    chat_request.admin_id = current_user["user_id"]

    db.commit()

    return RedirectResponse(
        "/admin/chat/requests",
        status_code=303,
    )
