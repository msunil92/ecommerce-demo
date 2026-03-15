from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db import get_db
from models import Product, OrderItem
from schemas import ProductCreate, ProductRead


templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_class=HTMLResponse)
def list_products_page(request: Request, db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .filter(Product.is_active.is_(True))
        .order_by(Product.name.asc())
        .all()
    )
    return templates.TemplateResponse(
        "products_list.html", {"request": request, "products": products}
    )


@router.get("/api", response_model=List[ProductRead])
def list_products_api(db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .filter(Product.is_active.is_(True))
        .order_by(Product.name.asc())
        .all()
    )
    return products


@router.post("/api", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(product_in: ProductCreate, db: Session = Depends(get_db)):
    product = Product(
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        stock=product_in.stock,
        is_active=product_in.is_active,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/api/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    in_use = db.query(OrderItem).filter(OrderItem.product_id == product_id).first()
    if in_use:
        raise HTTPException(
            status_code=400,
            detail="Product cannot be deleted because it is used in existing orders.",
        )

    db.delete(product)
    db.commit()

