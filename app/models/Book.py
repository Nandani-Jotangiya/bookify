from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    isbn = Column(String, unique=True, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)

    available_quantity = Column(
    Integer,
    nullable=False,
    default=0
    )
    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    category = relationship(
        "Category",
        back_populates="books"
    )

    book_requests = relationship(
        "BookRequest",
        back_populates="book"
    )

    issued_books = relationship(
    "IssuedBook",
    back_populates="book"
)