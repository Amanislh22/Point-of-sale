import datetime
import models
from pydantic import EmailStr
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, Float, String, UniqueConstraint, Enum, DateTime
from database import Base
from enums import ProgramType

class Program(Base):
    __tablename__ = 'program'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable = False)
    description = Column(String, nullable=False)
    program_type = Column(Enum(ProgramType), nullable=False)
    discount = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    product_buy_id = Column(Integer, ForeignKey(models.Product.id), nullable=True)
    product_get_id = Column(Integer, ForeignKey(models.Product.id), nullable=True)
    count = Column(Integer, nullable=True)

    _table_args__ = (
        UniqueConstraint('code', name='unique_code'),
        UniqueConstraint('email', name = 'unique_email_constraint'),
        CheckConstraint(
            "CASE "
            "WHEN type = 'DISCOUNT' THEN discount IS NOT NULL AND product_buy IS NULL AND product_get IS NULL AND count IS NULL "
            "ELSE discount IS NULL AND product_buy IS NOT NULL AND product_get IS NOT NULL AND count IS NOT NULL "
            "END",
            name='check_promotion_constraints'
        ),
    )

