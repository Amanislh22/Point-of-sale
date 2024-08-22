from enum import Enum as PyEnum
from pydantic import EmailStr
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String , Enum
from enums import AccountStatus, ContractType
from database import Base
from schemas import Gender
from sqlalchemy.orm import relationship

class Company(Base):
    __tablename__ = 'company'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    last_employee_number = Column(Integer, nullable=False)
    name = Column(String , nullable=False  )



