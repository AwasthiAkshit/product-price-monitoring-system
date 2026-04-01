# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True)
    name = Column(String)
    brand = Column(String)
    category = Column(String)
    source = Column(String)
    current_price = Column(Float)

    price_history = relationship("PriceHistory", back_populates="product")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_history")


class APIUser(Base):
    __tablename__ = "api_users"

    id = Column(Integer, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True)
    usage_count = Column(Integer, default=0)


class PriceEventLog(Base):
    __tablename__ = "price_events"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    old_price = Column(Float)
    new_price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
