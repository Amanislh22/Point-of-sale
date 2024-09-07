from sqlalchemy import Column, DateTime, ForeignKey, Integer, Enum
from database import Base
from models.employee import Employee
from enums.SessionStatus import SessionStatus

class Session(Base):
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True,autoincrement=True)
    opened_at = Column(DateTime , nullable=False)
    closed_at = Column(DateTime, nullable=True)
    employee_id = Column(Integer , ForeignKey(Employee.id) , nullable=False)
    session_status = Column(Enum(SessionStatus)  , nullable=True)

