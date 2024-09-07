from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, func
from database import Base
from models.customer import Customer
from models.session import Session
from sqlalchemy.orm import relationship

class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    number = Column(String, nullable=False)
    created_on = Column(DateTime, nullable=False, server_default=func.now())
    total_price = Column(Float, nullable=False)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=True)
    session_id = Column(Integer,ForeignKey(Session.id), nullable=False)
    order_lines = relationship("OrderLine", back_populates="order", lazy='select')

