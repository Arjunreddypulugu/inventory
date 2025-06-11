from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()

class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, index=True, nullable=False)
    manufacturer_part_number = Column(String, nullable=True)
    location = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True)
    manufacturer = Column(String, nullable=True)
    is_repeated = Column(Boolean, default=False)

class InventoryItemCreate(BaseModel):
    sku: str
    manufacturer_part_number: str = ""
    location: str = ""
    quantity: int = 0
    manufacturer: str = "" 