# erp-po-system

# ERP Purchase Order System

A simple web app to manage Vendors, Products, and Purchase Orders.

## Features
- Create & view vendors
- Create & view products
- Create purchase orders with multiple product rows
- Automatic total calculation with 5% tax
- Dashboard to view all purchase orders

## Database Design
- vendors → stores vendor details
- products → stores product info (name, sku, price, stock)
- purchase_orders → main order (vendor_id, total, status, date)
- purchase_order_items → each product row in an order

Why separate purchase_order_items?
Because one order can have multiple products. This keeps the design clean and normalized.

## How to Run

Backend:
1. cd backend
2. python -m venv venv
3. venv\Scripts\activate
4. pip install -r requirements.txt
5. create .env with DB credentials
6. python -m uvicorn main:app --reload

Frontend:
Open frontend/index.html using browser or Live Server

## APIs
- POST /vendors
- GET /vendors
- POST /products
- GET /products
- POST /purchase-orders
- GET /purchase-orders
- GET /purchase-orders/{id}

## Author
Medha Adepu
