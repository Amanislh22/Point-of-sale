from enum import Enum as PyEnum
from sqlalchemy import Column, ForeignKey, Integer, Enum, UniqueConstraint
from enums import Role
from database import Base
from sqlalchemy.orm import relationship

class EmployeeRole(Base):
    __tablename__ = 'employee_role'
    id = Column(Integer, primary_key=True, index=True, nullable=False,unique=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, unique=True)
    role = Column(Enum(Role), nullable=False )
    employee = relationship("Employee", foreign_keys=[employee_id], back_populates="roles", lazy="joined")
    __table_args__ = (
        UniqueConstraint('employee_id', 'role', name='uix_employee_role'),
    )
