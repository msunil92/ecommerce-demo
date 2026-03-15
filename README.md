# FastAPI E-commerce Demo

Minimal e‑commerce demo built with **FastAPI** and **SQLite**.

You can:

- Browse a small product catalog
- Place a demo order with shipping details
- View and mark orders as shipped from an admin page
- Create and delete products via JSON APIs

## Tech stack

- FastAPI
- SQLite via SQLAlchemy
- Jinja2 templates
- Uvicorn

## Getting started

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:

- Storefront: `http://127.0.0.1:8000/products`
- Admin orders: `http://127.0.0.1:8000/orders/admin/list`
- API docs: `http://127.0.0.1:8000/docs`

## Useful API calls

These are available from the interactive docs at `/docs` or any HTTP client:

- `GET /products/api` – list active products
- `POST /products/api` – create a product
- `DELETE /products/api/{product_id}` – delete a product (only if not used in orders)
- `POST /orders/api` – place an order with items
- `POST /orders/api/{order_id}/ship` – mark an order as shipped

Example: create a Samsung Mobile product:

```json
{
  "name": "Samsung Mobile",
  "description": "Latest Samsung smartphone",
  "price": 2090,
  "stock": 10,
  "is_active": true
}
```

