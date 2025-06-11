from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class InventoryItem(Base):
    __tablename__ = "StockOfParts"
    SKU = Column(String(255), primary_key=True, index=True)
    manufacturer_part_number = Column(String(255), nullable=True)
    Location = Column(String, nullable=True)
    Quantity = Column(String, nullable=True)
    manufacturer = Column(String(255), nullable=True)
    is_repeated = Column(String(255), default='no')

class InventoryItemCreate(BaseModel):
    SKU: str
    manufacturer_part_number: str = ""
    Location: str = ""
    Quantity: str = ""
    manufacturer: str = "" 