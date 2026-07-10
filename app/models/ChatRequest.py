from sqlalchemy import Integer, Column, ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ChatRequest(Base):
    __tablename__ = "chat_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    status = Column(String, default="pending")

    requested_at = Column(DateTime(timezone=True), server_default=func.now())

    approved_at = Column(DateTime(timezone=True), nullable=True)

    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

    admin = relationship("User", foreign_keys=[admin_id])

    messages = relationship(
        "ChatMessage", back_populates="chat_request", cascade="all, delete-orphan"
    )
