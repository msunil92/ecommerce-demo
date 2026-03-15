from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func

from db import Base, engine
from models import Product
from routers import products as products_router
from routers import orders as orders_router


app = FastAPI(title="Minimal E-commerce Store")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        products_count = conn.execute(
            select(func.count()).select_from(Product.__table__)
        ).scalar_one()
        if not products_count:
            sample_products = [
                {"name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price": 19.99, "stock": 50},
                {"name": "Mechanical Keyboard", "description": "Backlit mechanical keyboard", "price": 79.99, "stock": 30},
                {"name": "USB-C Hub", "description": "Multi-port USB-C hub", "price": 39.99, "stock": 40},
            ]
            conn.execute(Product.__table__.insert(), sample_products)


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/products")


app.include_router(products_router.router)
app.include_router(orders_router.router)

