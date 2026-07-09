from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.context import unread_notification_count
from app.core.dependencies import get_current_user, get_admin_user

from app.core.templates import render_template
from app.database import get_db
from app.models.Notification import Notification

router = APIRouter()


@router.get("/notifications")
def notifications(
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    notification_count = unread_notification_count(
        db,
        current_user["user_id"],
    )

    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user["user_id"])
        .order_by(Notification.created_at.desc())
        .all()
    )

    return render_template(
        request,
        "user/notifications.html",
        user=current_user,
        notifications=notifications,
        unread_notification_count=notification_count,
    )


@router.post("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_current_user(request)

    if not current_user:
        return RedirectResponse("/login", status_code=303)

    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user["user_id"],
        )
        .first()
    )

    if not notification:
        return RedirectResponse("/notifications", status_code=303)

    notification.is_read = True
    db.commit()

    return RedirectResponse("/notifications", status_code=303)


@router.post("/admin/notifications/read-all")
def mark_all_admin_notifications_as_read(
    request: Request,
    db: Session = Depends(get_db),
):
    current_admin = get_admin_user(request)

    if not current_admin:
        return RedirectResponse("/login", status_code=303)

    (
        db.query(Notification)
        .filter(
            Notification.user_id == current_admin["user_id"],
            Notification.is_read.is_(False),
        )
        .update(
            {"is_read": True},
            synchronize_session=False,
        )
    )

    db.commit()

    return RedirectResponse(
        "/admin/notifications",
        status_code=303,
    )
