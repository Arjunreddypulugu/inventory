from sqlalchemy.orm import Session
from . import models

def add_inventory_item(db: Session, item: models.InventoryItemCreate):
    exists = db.query(models.InventoryItem).filter(models.InventoryItem.SKU == item.SKU).first()
    if exists:
        return {"is_repeated": "yes", "SKU": item.SKU}
    db_item = models.InventoryItem(
        SKU=item.SKU,
        manufacturer_part_number=item.manufacturer_part_number,
        Location=item.Location,
        Quantity=item.Quantity,
        manufacturer=item.manufacturer,
        is_repeated="no"
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"is_repeated": "no", "SKU": db_item.SKU} 