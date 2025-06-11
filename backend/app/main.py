from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, crud, db

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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