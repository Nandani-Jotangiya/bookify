from sqlalchemy import Column,Integer,ForeignKey,String,DateTime
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class IssuedBook(Base):
    __tablename__ = "issued_books"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    book_id = Column(Integer,ForeignKey("books.id"),nullable=False)
    issued_date = Column(DateTime,default=func.now())
    due_date = Column(DateTime)
    status = Column(String,default="issued")

    user = relationship("User")
    book = relationship("Book")