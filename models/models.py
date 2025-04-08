from sqlalchemy import DateTime, Table,Column, Text, DECIMAL, func
from sqlalchemy.types import Integer,String
from config.db import meta
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    email = Column(String(255))
    password = Column(String(255))

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key = True, index= True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10,2), nullable=False)
    stock_quantity = Column(Integer, nullable=False)

class Flower(Base):
    __tablename__ = 'flowers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    # image_url sẽ lưu đường dẫn tương đối tới file trên server, ví dụ: /media/flower_images/abc.jpg
    image_url = Column(String(255), nullable=True)
    flower_type = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    
