from enum import Enum as PyEnum
from sqlalchemy import Column, ForeignKey, Integer, Enum, String
from enums import Role
from database import Base
from sqlalchemy.orm import relationship

class JWTBlacklist(Base):
    __tablename__ = 'JWT_Blacklist'
    id = Column(Integer, primary_key=True, index=True, nullable=False,unique=True,autoincrement=True)
    token = Column(String, nullable=False)
