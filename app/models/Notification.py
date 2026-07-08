from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    String,
    Boolean,
    Text,
    DateTime,
    Enum as SQLEnum,
)
from app.database import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.enums.notification_type import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(255), nullable=False)

    notification_type = Column(
        SQLEnum(NotificationType),
        nullable=False,
    )

    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="notifications")
