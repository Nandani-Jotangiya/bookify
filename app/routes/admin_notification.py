from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Notification import Notification
from app.core.dependencies import get_admin_user
from app.core.templates import render_template
from app.core.context import unread_admin_notification_count

router = APIRouter()


@router.get("/admin/notifications")
def admin_notifications(
    request: Request,
    db: Session = Depends(get_db),
):
    current_admin = get_admin_user(request)

    if not current_admin:
        return RedirectResponse("/login", status_code=303)

    notification_count = unread_admin_notification_count(
        db,
        current_admin["user_id"],
    )
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_admin["user_id"])
        .order_by(Notification.created_at.desc())
        .all()
    )

    return render_template(
        request,
        "admin/notifications.html",
        user=current_admin,
        notifications=notifications,
        unread_notification_count=notification_count,
    )


@router.post("/admin/notifications/{notification_id}/read")
def mark_admin_notification_as_read(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current_admin = get_admin_user(request)

    if not current_admin:
        return RedirectResponse("/login", status_code=303)

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_admin["user_id"],
        )
        .first()
    )
    if not notification:
        return RedirectResponse(
            "/admin/notifications",
            status_code=303,
        )

    notification.is_read = True

    db.commit()

    return RedirectResponse(
        "/admin/notifications",
        status_code=303,
    )
