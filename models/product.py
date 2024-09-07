from sqlalchemy import Column, ForeignKey, Integer, String, Float
from database import Base
from models.category import Category

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    name = Column(String, nullable=False , unique=True)
    description = Column(String, nullable=True)
    unit_price = Column(Float, nullable=False )
    quantity = Column(Integer, nullable=False )
    image_link = Column(String, nullable=True )
    category_id = Column(Integer, ForeignKey(Category.id), nullable=False)


