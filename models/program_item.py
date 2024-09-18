import models
from pydantic import EmailStr
from sqlalchemy import Column, ForeignKey, Integer, String, Enum
from database import Base
import enums


class ProgramItem(Base):
    __tablename__ = 'program_item'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    code = Column(String, unique=True, nullable = False)
    code_status = Column(Enum(enums.codeStatus), nullable=  False, default=enums.codeStatus.active)
    program_id = Column(Integer, ForeignKey(models.Program.id), nullable=False)
    order_id = Column(Integer,ForeignKey(models.Order.id), nullable=True, default=None)
