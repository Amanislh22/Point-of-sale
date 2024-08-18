from sqlalchemy import Column, Integer, String, DateTime
from pydantic import EmailStr
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String , Enum
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Error(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, nullable=False)
    orig = Column(String, nullable=False)
    params = Column(String, nullable=False)
    statement = Column(String, nullable=False)
    created_on = Column(DateTime,nullable=False, server_default=func.now())
