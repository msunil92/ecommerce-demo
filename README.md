# FastAPI E-commerce Demo

Minimal e‑commerce demo built with **FastAPI** and **SQLite**.

You can:

- Browse a small product catalog
- Place a demo order with shipping details
- View and mark orders as shipped from an admin page

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

