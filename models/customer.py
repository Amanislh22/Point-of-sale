from sqlalchemy import  Column, Integer, String, UniqueConstraint
from database import Base

class Customer(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False , unique=True)
    __table_args__ = (
        UniqueConstraint('email', name = 'unique_email_constraint'),)

