-- Users table for both vendors and suppliers
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('vendor', 'supplier')), -- 'vendor' or 'supplier'
    name TEXT,                  -- User's full name
    shop_business_name TEXT,    -- Vendor's shop name or Supplier's business name
    locality TEXT,              -- E.g., 'Dadar Market', 'Malad West'
    contact_number TEXT
);

-- Products available in the system (e.g., Potato, Onion, Rice)
DROP TABLE IF EXISTS products;
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    unit TEXT NOT NULL,         -- E.g., 'kg', 'dozen', 'piece', 'liter'
    category TEXT               -- E.g., 'Vegetable', 'Fruit', 'Spice', 'Grain', 'Oil'
);

-- Mapping between suppliers and the products they offer, including their prices
DROP TABLE IF EXISTS supplier_products;
CREATE TABLE supplier_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    price_per_unit REAL NOT NULL,
    stock INTEGER DEFAULT -1,   -- -1 implies unlimited stock for simplicity; can be >0
    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id),
    UNIQUE (supplier_id, product_id) -- A supplier offers a specific product only once
);

-- Main Orders table
DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL, -- The specific supplier for this order
    order_date TEXT DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Pending', -- 'Pending', 'Confirmed', 'Delivered', 'Cancelled'
    total_amount REAL,
    FOREIGN KEY (vendor_id) REFERENCES users (id),
    FOREIGN KEY (supplier_id) REFERENCES users (id)
);

-- Details of each item within an order
DROP TABLE IF EXISTS order_items;
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
    price_at_order REAL NOT NULL, -- Price when ordered (important for historical accuracy)
    FOREIGN KEY (order_id) REFERENCES orders (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);