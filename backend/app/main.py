from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, crud, db
from fastapi.responses import FileResponse
import pandas as pd
import os

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

@app.get("/inventory/download")
def download_inventory(database: Session = Depends(get_db)):
    # Query all rows
    items = database.execute("SELECT * FROM StockOfParts").fetchall()
    columns = [col[0] for col in database.execute("SELECT * FROM StockOfParts").cursor.description]
    df = pd.DataFrame(items, columns=columns)
    file_path = "inventory_export.xlsx"
    df.to_excel(file_path, index=False)
    return FileResponse(file_path, filename="inventory_export.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") 