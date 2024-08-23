from enum import Enum
from pydantic import EmailStr
from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String , Enum, UniqueConstraint
from enums import AccountStatus, ContractType
from database import Base
from schemas import Gender
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    number = Column(Integer, nullable=False , unique=True)
    phone_number = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    cnss_number = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    gender = Column(Enum(Gender), nullable=False)
    status = Column(Enum(AccountStatus), nullable=False , default=AccountStatus.inactive)
    contract_type = Column(Enum(ContractType), nullable=False)
    password = Column(String, nullable=True)
    company_id = Column(Integer,ForeignKey("company.id"), nullable=False )
    company = relationship("Company",foreign_keys=[company_id], lazy="joined")
    roles = relationship("EmployeeRole", back_populates="employee", lazy="joined")
    __table_args__ = (
        UniqueConstraint('cnss_number', name='unique_cnss_number'),
        UniqueConstraint('email', name = 'unique_email_constraint'),
        CheckConstraint(
            "(contract_type IN ('cdi', 'cdd') AND cnss_number IS NOT NULL AND cnss_number ~ '^\\d{8}-\\d{2}$') OR "
            "(contract_type IN ('apprenti', 'sivp') AND (cnss_number IS NULL OR cnss_number ~ '^\\d{8}-\\d{2}$'))",
            name='check_contract_type_and_cnss_number'
        ),
    )

