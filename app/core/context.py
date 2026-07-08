# app/core/context.py

from sqlalchemy.orm import Session
from app.models.Notification import Notification


def unread_notification_count(db: Session, user_id: int):
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .count()
    )


def unread_admin_notification_count(db, admin_id):
    return (
        db.query(Notification)
        .filter(
            Notification.user_id == admin_id,
            Notification.is_read.is_(False),
        )
        .count()
    )
