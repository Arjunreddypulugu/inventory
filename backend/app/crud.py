from sqlalchemy.orm import Session
from . import models, db

def add_inventory_item(db: Session, item: models.InventoryItemCreate):
    # Create a new session for checking existence
    check_session = db.SessionLocal()
    try:
        # Check if SKU exists to determine is_repeated value
        exists = check_session.query(models.InventoryItem).filter(models.InventoryItem.SKU == item.SKU).first()
        is_repeated = "yes" if exists else "no"
    finally:
        check_session.close()
    
    # Create new entry in the main session
    db_item = models.InventoryItem(
        SKU=item.SKU,
        manufacturer_part_number=item.manufacturer_part_number,
        Location=item.Location,
        Quantity=item.Quantity,
        manufacturer=item.manufacturer,
        is_repeated=is_repeated
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"is_repeated": is_repeated, "SKU": db_item.SKU} 