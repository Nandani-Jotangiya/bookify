from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class IssuedBook(Base):
    __tablename__ = "issued_books"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=False
    )

    request_id = Column(
        Integer,
        ForeignKey("book_requests.id"),
        nullable=False
    )

    issued_date = Column(
        DateTime,
        default=func.now()
    )

    due_date = Column(DateTime)

    return_date = Column(DateTime)

    status = Column(
        String,
        default="issued"
    )

    user = relationship(
        "User",
        back_populates="issued_books"
    )

    book = relationship(
        "Book",
        back_populates="issued_books"
    )