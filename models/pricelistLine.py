from enum import Enum as PyEnum
from pydantic import EmailStr
from sqlalchemy import CheckConstraint, Column, DateTime, Float, ForeignKey, Integer
from database import Base
from sqlalchemy.orm import relationship
from models.pricelist import Pricelist
from models.product import Product

class PricelistLine(Base):
    __tablename__ = 'pricelistLine'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    new_price = Column(Float, nullable = False)
    min_quantity = Column(Integer , nullable = False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime , nullable=False)
    pricelist_id = Column(Integer, ForeignKey(Pricelist.id), nullable=False)
    product_id = Column(Integer, ForeignKey(Product.id), nullable=False)
    __table_args__ = (
        CheckConstraint('start_date <= end_date', name='check_start_end_date'),
    )

