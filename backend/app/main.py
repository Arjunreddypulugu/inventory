from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models, crud, db

app = FastAPI()

# Dependency
def get_db():
    database = db.SessionLocal()
    try:
        yield database
    finally:
        database.close()

@app.post("/inventory/add")
def add_inventory(item: models.InventoryItemCreate, database: Session = Depends(get_db)):
    result = crud.add_inventory_item(database, item)
    return result 