from pydantic import EmailStr
from sqlalchemy import Column, Integer, String
from database import Base

class Pricelist(Base):
    __tablename__ = 'pricelist'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    name = Column(String , nullable =False)
    description = Column(String , nullable =False)

