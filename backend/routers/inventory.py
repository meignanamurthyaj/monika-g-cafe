from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from decimal import Decimal

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

@router.post("/ingredients")
def add_ingredient(ingredient: schemas.IngredientCreate, db: Session = Depends(get_db)):
    db_ingredient = models.Ingredient(**ingredient.model_dump())
    db.add(db_ingredient)
    db.commit()
    db.refresh(db_ingredient)
    return {"message": "Ingredient added", "id": db_ingredient.ingredient_id}

@router.get("/alerts")
def get_low_stock_alerts(db: Session = Depends(get_db)):
    low_stock = db.query(models.Ingredient).filter(models.Ingredient.stock_level <= models.Ingredient.low_stock_threshold).all()
    return low_stock

@router.patch("/ingredients/{id}/restock")
def restock_ingredient(id: int, amount: float, db: Session = Depends(get_db)):
    item = db.query(models.Ingredient).filter(models.Ingredient.ingredient_id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    amount = Decimal(str(amount))
    item.stock_level += amount
    db.commit()
    return {"message": "Stock updated", "new_level": item.stock_level}

from decimal import Decimal

