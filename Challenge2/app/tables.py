from sqlalchemy import Column, Integer, String, Float, Date, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)