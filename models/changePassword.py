from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String , Enum
from enums import TokenStatus
from database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class ChangePassword(Base):
    __tablename__ = 'change_password'
    id = Column(Integer, primary_key=True, index=True, nullable=False,autoincrement=True)
    token = Column(String, nullable=False)
    status = Column(Enum(TokenStatus), nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", foreign_keys=[employee_id], lazy="joined")
