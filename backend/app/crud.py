from sqlalchemy.orm import Session
from . import models

def add_inventory_item(db: Session, item: models.InventoryItemCreate):
    # Check if SKU exists
    exists = db.query(models.InventoryItem).filter(models.InventoryItem.sku == item.sku).first()
    is_repeated = bool(exists)
    db_item = models.InventoryItem(
        sku=item.sku,
        manufacturer_part_number=item.manufacturer_part_number,
        location=item.location,
        quantity=item.quantity,
        manufacturer=item.manufacturer,
        is_repeated=is_repeated
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item 