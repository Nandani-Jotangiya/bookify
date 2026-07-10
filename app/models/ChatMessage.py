from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)

    chat_request_id = Column(
        Integer, ForeignKey("chat_requests.id"), nullable=False, index=True
    )
    sender_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    receiver_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)

    message = Column(Text, nullable=False)

    is_read = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat_request = relationship("ChatRequest", back_populates="messages")

    sender = relationship("User", foreign_keys=[sender_id])

    receiver = relationship("User", foreign_keys=[receiver_id])
