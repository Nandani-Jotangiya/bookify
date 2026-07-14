from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.dependencies import get_current_user
from app.core.templates import render_template
from app.core.context import get_user_context

from app.models.ChatRequest import ChatRequest
from app.models.ChatMessage import ChatMessage

router = APIRouter()


@router.get("/user/chat")
def user_chat(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Only users can access
    if current_user["role"] != "user":
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    chat_request = (
        db.query(ChatRequest)
        .filter(ChatRequest.user_id == current_user["user_id"])
        .order_by(ChatRequest.requested_at.desc())
        .first()
    )

    context = get_user_context(
        db=db,
        current_user=current_user,
    )

    context.update(
        {
            "user": current_user,
            "chat_request": chat_request,
        }
    )

    return render_template(
        request=request,
        name="user/chat.html",
        **context,
    )


@router.post("/user/chat/request")
def request_chat(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Only users can request chat
    if current_user["role"] != "user":
        return RedirectResponse(
            url="/",
            status_code=303,
        )

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
    db.refresh(new_request)

    return RedirectResponse(
        url="/user/chat",
        status_code=303,
    )


@router.get("/user/chat/messages")
def chat_messages(
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Only users can access
    if current_user["role"] != "user":
        return RedirectResponse(
            url="/",
            status_code=303,
        )

    chat_request = (
        db.query(ChatRequest)
        .filter(
            ChatRequest.user_id == current_user["user_id"],
            ChatRequest.status == "approved",
        )
        .order_by(ChatRequest.approved_at.desc())
        .first()
    )

    if not chat_request:
        return RedirectResponse(
            url="/user/chat",
            status_code=303,
        )
        # Mark all unread messages as read
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

    db.commit()

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_request_id == chat_request.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    context = get_user_context(
        db=db,
        current_user=current_user,
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
        name="user/chat_messages.html",
        **context,
    )
