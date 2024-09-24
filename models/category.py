from sqlalchemy import Column, Integer, String
from database import Base

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer , primary_key=True , autoincrement=True)
    name = Column(String ,nullable=False)
    description = Column(String , nullable =False)
    icon_name = Column(String , nullable=False)
