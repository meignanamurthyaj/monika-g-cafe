from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas
# Change your import on line 6 to this:
from backend.utils.auth import get_current_user, RoleRequirement

router = APIRouter(prefix="/orders", tags=["Order Management"])

@router.post("/", response_model=dict)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(
        customer_id=order_data.customer_id,
        table_id=order_data.table_id,
        order_type=order_data.order_type,
        order_status="Pending"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    new_status
    for item in order_data.items:
        order_item = models.OrderItem(
            order_id=new_order.order_id,
            item_id=item.item_id,
            quantity=item.quantity,
            unit_price=item.unit_price
        )
        db.add(order_item)
        
        # Deduct inventory stock based on recipes if configured
        recipe_ingredients = db.query(models.MenuItemIngredient).filter(models.MenuItemIngredient.item_id == item.item_id).all()
        for recipe in recipe_ingredients:
            ingredient = db.query(models.Ingredient).filter(models.Ingredient.ingredient_id == recipe.ingredient_id).first()
            if ingredient:
                ingredient.stock_level -= (recipe.quantity_required * item.quantity)
                
    db.commit()
    return {"message": "Order placed successfully", "order_id": new_order.order_id}

@router.get("/")
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()

@router.put("/{order_id}/status")
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.order_status = status
    db.commit()
    return {"message": f"Order status updated to {status}"}

@router.patch("/{order_id}/status")
def update_order_status(
    order_id: int, 
    new_status: str, 
    db: Session = Depends(get_db),
    current_user = Depends(RoleRequirement(["Admin", "Manager", "Staff"]))
):
    # Valid tracking statuses matching your database schema enum
    valid_statuses = ["Pending", "In Kitchen", "Ready", "Completed", "Cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid target operational status value.")

    # Locate order inside database index lookup
    order = db.query(models).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Requested order resource not found.")

    # Mutate and commit the status field change
    order.status = new_status
    db.commit()
    
    return {"message": f"Order #{order_id} status updated to '{new_status}' successfully."}