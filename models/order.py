from sqlalchemy import Column, Integer, String, Float
from utils.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    total_amount = Column(Float)
    currency = Column(String)
    status = Column(String, default="pending")

