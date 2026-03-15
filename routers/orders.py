from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from db import get_db
from models import Order, OrderItem, OrderStatusEnum, Product
from schemas import OrderCreate, OrderItemCreate, OrderRead


templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/orders", tags=["orders"])


def _create_order(db: Session, order_in: OrderCreate) -> Order:
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item.")

    product_ids = {item.product_id for item in order_in.items}
    products = (
        db.query(Product)
        .filter(Product.id.in_(product_ids), Product.is_active.is_(True))
        .all()
    )
    products_by_id = {p.id: p for p in products}

    if len(products_by_id) != len(product_ids):
        raise HTTPException(status_code=400, detail="Some products are invalid or inactive.")

    for item in order_in.items:
        product = products_by_id[item.product_id]
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}'.",
            )

    order = Order(
        customer_name=order_in.customer_name,
        customer_email=order_in.customer_email,
        shipping_address=order_in.shipping_address,
    )
    db.add(order)
    db.flush()

    for item in order_in.items:
        product = products_by_id[item.product_id]
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=float(product.price),
        )
        db.add(order_item)
        product.stock -= item.quantity

    db.commit()
    db.refresh(order)
    return order


@router.post("/api", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order_api(order_in: OrderCreate, db: Session = Depends(get_db)):
    order = _create_order(db, order_in)
    return order


@router.get("/{order_id}", response_class=HTMLResponse)
def get_order_page(order_id: int, request: Request, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    return templates.TemplateResponse(
        "order_confirmation.html",
        {"request": request, "order": order},
    )


@router.get("/admin/list", response_class=HTMLResponse)
def list_orders_admin(request: Request, db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(100).all()
    return templates.TemplateResponse(
        "orders_admin.html", {"request": request, "orders": orders}
    )


@router.post("/{order_id}/ship")
def mark_order_shipped(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    order.status = OrderStatusEnum.SHIPPED.value
    db.commit()
    return RedirectResponse(
        url="/orders/admin/list", status_code=status.HTTP_303_SEE_OTHER
    )


@router.post("/api/{order_id}/ship", response_model=OrderRead)
def mark_order_shipped_api(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")
    order.status = OrderStatusEnum.SHIPPED.value
    db.commit()
    db.refresh(order)
    return order


@router.post("/place", response_class=HTMLResponse)
def place_order_from_form(
    request: Request,
    customer_name: str = Form(...),
    customer_email: str = Form(...),
    shipping_address: str = Form(...),
    product_ids: List[int] = Form(...),
    quantities: List[int] = Form(...),
    db: Session = Depends(get_db),
):
    items: List[OrderItemCreate] = []
    for product_id, qty in zip(product_ids, quantities):
        qty_int = int(qty)
        if qty_int > 0:
            items.append(OrderItemCreate(product_id=product_id, quantity=qty_int))

    if not items:
        raise HTTPException(status_code=400, detail="No items selected.")

    order_in = OrderCreate(
        customer_name=customer_name,
        customer_email=customer_email,
        shipping_address=shipping_address,
        items=items,
    )
    order = _create_order(db, order_in)
    return RedirectResponse(
        url=f"/orders/{order.id}", status_code=status.HTTP_303_SEE_OTHER
    )

