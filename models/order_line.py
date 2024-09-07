from sqlalchemy import Column, Float, ForeignKey, Integer
from database import Base
from models.order import Order
from models.product import Product
from sqlalchemy.orm import relationship

class OrderLine(Base):
    __tablename__ = 'order_line'
    id = Column(Integer ,  primary_key=True,autoincrement=True)
    unit_price = Column(Float , nullable=False)
    quantity = Column(Integer,nullable=False)
    total_price = Column(Float , nullable=False)
    order_id =Column(Integer, ForeignKey(Order.id),nullable=False)
    product_id =Column(Integer, ForeignKey(Product.id),nullable=False)
    order = relationship("Order", back_populates="order_lines")
