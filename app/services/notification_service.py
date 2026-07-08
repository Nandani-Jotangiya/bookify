from sqlalchemy.orm import Session

from app.enums.notification_type import NotificationType
from app.models.Notification import Notification


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: NotificationType,
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
    )
    db.add(notification)
    db.commit()

    db.refresh(notification)

    return notification
