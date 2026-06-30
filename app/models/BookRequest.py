from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship


class BookRequest(Base):
    __tablename__ = "book_requests"

    id = Column(Integer, primary_key=True, unique=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)

    status = Column(String, default="pending")
    rental_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="book_requests")
    book = relationship("Book", back_populates="book_requests")
