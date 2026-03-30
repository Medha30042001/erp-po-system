from fastapi import FastAPI
from db import get_connection
from schemas import VendorCreate, ProductCreate, PurchaseOrderCreate
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://erp-po-system.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get('/')
def home():
    return {"message" : "ERP PO System API is running"}

@app.get('/test-db')
def test_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {"db_time" : result}

#-----------------------------------------------------------------------

@app.post('/vendors')
def create_vendors(vendor: VendorCreate):
    conn = get_connection()
    cursor = conn.cursor()

    query = """INSERT INTO vendors (name, contact, rating) 
                VALUES (%s, %s, %s)
                RETURNING id, name, contact, rating;"""

    cursor.execute(query, (vendor.name, vendor.contact, vendor.rating))
    new_vendor = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message" : "Vendor created successfully",
        "vendor" : {
            "id" : str(new_vendor[0]),
            "name" : new_vendor[1],
            "contact" : new_vendor[2],
            "rating" : float(new_vendor[3]) if new_vendor[3] is not None else None
        }
    }

#-------------------------------------------------------------------------

@app.get('/vendors')
def get_vendors():
    conn = get_connection()
    cursor = conn.cursor()

    query = """SELECT * FROM vendors
            ORDER BY name;"""

    cursor.execute(query)
    vendors = cursor.fetchall()

    cursor.close()
    conn.close()

    vendors_list = []

    for vendor in vendors:
        vendors_list.append({
            "id" : str(vendor[0]),
            "name" : vendor[1],
            "contact" : vendor[2],
            "rating" : float(vendor[3]) if vendor[3] is not None else None
        })

    return {
        "vendors" : vendors_list
    }

#-------------------------------------------------------------------------

@app.post('/products')
def create_products(product: ProductCreate):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            INSERT INTO products (name, sku, unit_price, stock_level) 
            VALUES (%s, %s, %s, %s)
            RETURNING id, name, sku, unit_price, stock_level;
            """
    
    cursor.execute(
        query,
        (product.name, product.sku, product.unit_price, product.stock_level)
    )
    new_product = cursor.fetchone()

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message" : "Product created successfully",
        "product" : {
            "id" : str(new_product[0]),
            "name" : new_product[1],
            "sku" : new_product[2],
            "unit_price" : float(new_product[3]),
            "stock_level" : new_product[4]
        }
    }

#--------------------------------------------------------------------------

@app.get('/products')
def get_products():
    conn = get_connection()
    cursor = conn.cursor()

    query = """SELECT * FROM products ORDER BY name;"""

    cursor.execute(query)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    products_list = []

    for product in products:
        products_list.append({
            "id" : str(product[0]),
            "name" : product[1],
            "sku" : product[2],
            "unit_price" : float(product[3]),
            "stock_level" : product[4]
        })

    return {"products" : products_list}

#-------------------------------------------------------------------------

@app.post('/purchase-orders')
def create_purchase_order(order: PurchaseOrderCreate):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        subtotal = 0
        item_details = []

        for item in order.items:
            cursor.execute(
                """
                SELECT id, name, unit_price
                FROM products
                WHERE id = %s;
                """,
                (item.product_id,)
            )

            product = cursor.fetchone()

            if not product:
                cursor.close()
                conn.close()
                return {"error": f"Product with id {item.product_id} not found"}

            unit_price = float(product[2])
            line_total = unit_price * item.quantity
            subtotal += line_total

            item_details.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "line_total": line_total
            })

        tax = subtotal * 0.05
        total_amount = subtotal + tax

        reference_no = f"PO-{uuid4().hex[:8].upper()}"

        cursor.execute(
            """
            INSERT INTO purchase_orders (reference_no, vendor_id, total_amount, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id, reference_no, vendor_id, total_amount, status, created_at;
            """,
            (reference_no, order.vendor_id, total_amount, "Pending")
        )

        new_order = cursor.fetchone()
        purchase_order_id = new_order[0]

        for item in item_details:
            cursor.execute(
                """
                INSERT INTO purchase_order_items
                (purchase_order_id, product_id, quantity, unit_price, line_total)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (
                    purchase_order_id,
                    item["product_id"],
                    item["quantity"],
                    item["unit_price"],
                    item["line_total"]
                )
            )

        conn.commit()

        return {
            "message": "Purchase order created successfully",
            "purchase_order": {
                "id": str(new_order[0]),
                "reference_no": new_order[1],
                "vendor_id": str(new_order[2]),
                "subtotal": subtotal,
                "tax": tax,
                "total_amount": float(new_order[3]),
                "status": new_order[4]
            },
            "items": item_details
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()
#--------------------------------------------------------------------------

@app.get('/purchase-orders')
def get_purchase_orders():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
            SELECT
                po.id,
                po.reference_no,
                po.vendor_id,
                v.name AS vendor_name,
                po.total_amount,
                po.status,
                po.created_at
            FROM purchase_orders po
            INNER JOIN vendors v
                ON po.vendor_id = v.id
            ORDER BY po.created_at DESC;
            """

    cursor.execute(query)
    orders = cursor.fetchall()

    orders_list = []

    for order in orders:
        orders_list.append({
            "id" : str(order[0]),
            "reference_no" : order[1],
            "vendor_id" : str(order[2]),
            "vendor_name" : order[3],
            "total_amount" : float(order[4]),
            "status" : order[5],
            "created_at" : order[6]
        })
    
    return {"purchase_orders" : orders_list}

#------------------------------------------------------------------------

@app.get('/purchase-orders/{order_id}')
def get_purchase_order_by_id(order_id : str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 
            po.id,
            po.reference_no,
            po.vendor_id,
            v.name AS vendor_name,
            po.total_amount,
            po.status,
            po.created_at
        FROM purchase_orders po
        INNER JOIN vendors v
            ON po.vendor_id = v.id
        WHERE po.id = %s;
        """,
        (order_id,)
    )

    order = cursor.fetchone()

    if not order:
        cursor.close()
        conn.close()
        return {"error" : "Purchase order not found"}

    cursor.execute(
        """
        SELECT 
            poi.product_id,
            p.name AS product_name,
            poi.quantity,
            poi.unit_price,
            poi.line_total
        FROM purchase_order_items poi
        INNER JOIN products p 
            ON poi.product_id = p.id
        WHERE poi.purchase_order_id = %s;
        """,
        (order_id,)
    )

    items = cursor.fetchall()

    cursor.close()
    conn.close()

    items_list = []

    for item in items:
        items_list.append({
            "product_id" : str(item[0]),
            "product_name" : item[1],
            "quantity" : item[2],
            "unit_price" : float(item[3]),
            "line_total" : float(item[4])
        })

    return{
        "purchase_order": {
            "id" : str(order[0]),
            "reference_no" : order[1],
            "vendor_id" : str(order[2]),
            "vendor_name" : order[3],
            "total_amount" : float(order[4]),
            "status" : order[5],
            "created_at" : order[6]
        },
        "items" : items_list
    }