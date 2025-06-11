from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class InventoryItem(Base):
    __tablename__ = "StockOfParts"
    SKU = Column(String, primary_key=True, index=True)
    manufacturer_part_number = Column(String, nullable=True)
    Location = Column(String, nullable=True)
    Quantity = Column(Integer, nullable=True)
    manufacturer = Column(String, nullable=True)
    is_repeated = Column(String, default='no')

class InventoryItemCreate(BaseModel):
    SKU: str
    manufacturer_part_number: str = ""
    Location: str = ""
    Quantity: int = 0
    manufacturer: str = "" 