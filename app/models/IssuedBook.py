from sqlalchemy import (
    Column,
    Integer,
    Float,
    ForeignKey,
    String,
    DateTime,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class IssuedBook(Base):
    __tablename__ = "issued_books"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    book_id = Column(
        Integer,
        ForeignKey("books.id"),
        nullable=False,
    )

    request_id = Column(
        Integer,
        ForeignKey("book_requests.id"),
        nullable=False,
    )

    issued_date = Column(
        DateTime,
        default=func.now(),
    )

    rent_amount = Column(
        Float,
        default=0,
    )

    deposit_amount = Column(
        Float,
        default=0,
    )

    deposit_paid = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    deposit_paid_date = Column(
        DateTime,
        nullable=True,
    )

    late_days = Column(
        Integer,
        default=0,
    )

    fine_amount = Column(
        Float,
        default=0,
    )

    fine_paid = Column(
        Boolean,
        default=False,
    )

    fine_paid_date = Column(
        DateTime,
        nullable=True,
    )

    due_date = Column(
        DateTime,
        nullable=False,
    )

    return_date = Column(
        DateTime,
        nullable=True,
    )

    STATUS_PENDING = "pending"
    STATUS_ISSUED = "issued"
    STATUS_RETURNED = "returned"

    status = Column(
        String,
        default=STATUS_ISSUED,
    )

    user = relationship(
        "User",
        back_populates="issued_books",
    )

    book = relationship(
        "Book",
        back_populates="issued_books",
    )