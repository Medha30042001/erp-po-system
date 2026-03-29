CREATE TABLE vendors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  contact TEXT NOT NULL,
  rating NUMERIC(2, 1) CHECK (rating >= 0 AND rating <= 5)
);

SELECT * FROM vendors;

CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  sku TEXT UNIQUE NOT NULL,
  unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
  stock_level INT NOT NULL CHECK (stock_level >= 0)
);

SELECT * FROM products;

CREATE TABLE purchase_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reference_no TEXT UNIQUE NOT NULL,
  vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
  total_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'Pending',
  created_at TIMESTAMPTZ DEFAULT now()
);

SELECT * FROM purchase_orders;

CREATE TABLE purchase_order_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  purchase_order_id UUID NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  quantity INT NOT NULL,
  unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
  line_total NUMERIC(12, 2) NOT NULL CHECK (line_total >= 0)
);

SELECT * FROM purchase_order_items;

INSERT INTO vendors (name, contact, rating)
VALUES 
('OfficeMart Pvt Ltd', 'office@mart.com', 4.5),
('Tech Supplies Co', 'tech@supplies.com', 4.2),
('Stationery Hub', 'stationery@hub.com', 4.8),
('Global Industrial', 'sales@global.com', 4.1);

INSERT INTO products (name, sku, unit_price, stock_level)
VALUES 
('Keyboard', 'KEY001', 500, 50),
('Mouse', 'MOU001', 300, 80),
('Monitor', 'MON001', 8000, 20),
('USB Cable', 'USB001', 150, 200),
('Printer', 'PRI001', 12000, 10),
('Notebook Pack', 'NOTE001', 250, 150);