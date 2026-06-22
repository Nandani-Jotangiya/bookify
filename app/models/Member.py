from sqlalchemy import Integer, String, Text, Column,DateTime
from sqlalchemy.sql import func
from app.database import Base

class Member (Base):
    __tablename__ = "members"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,nullable=False)
    email = Column(String,unique=True,nullable=False)
    phone = Column(String,nullable=False)
    address = Column(Text)
    status = Column(String,default="Active")
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    