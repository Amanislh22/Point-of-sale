from datetime import datetime
from sqlalchemy import Column, DateTime, Enum , ForeignKey, Integer, String
from database import Base
from enums import TokenStatus
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class AccountActivation(Base):
    __tablename__ = 'account_activation'
    id = Column(Integer, primary_key=True, index=True, nullable=False,autoincrement=True)
    email = Column(String, nullable=False, unique=True)
    token = Column(String, nullable=False)
    status = Column(Enum(TokenStatus), nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    employee = relationship("Employee", foreign_keys=[employee_id], lazy="joined")
