import sqlite3
from werkzeug.security import generate_password_hash
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database.db')
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), 'schema.sql')

def get_db_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_schema():
    """Initializes database schema from schema.sql."""
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()
    print("Database schema initialized.")

def populate_initial_data():
    """Populates the database with dummy users, products, and supplier offerings."""
    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        # 1. Add Dummy Users (Vendors and Suppliers)
        # Passwords for all users are 'password123'
        users_data = [
            ('vendor1', generate_password_hash('password123'), 'vendor', 'Rohan Singh', 'Rohan\'s Vada Pav', 'Dadar Market', '9876543210'),
            ('supplier1', generate_password_hash('password123'), 'supplier', 'Amit Sharma', 'Fresh Veggies Co.', 'Dadar Wholesale', '9988776655'), # Main Veggie
            ('vendor2', generate_password_hash('password123'), 'vendor', 'Priya Patel', 'Priya Snacks', 'Churchgate', '9123456789'),
            ('supplier2', generate_password_hash('password123'), 'supplier', 'Sunil Kumar', 'Spice World', 'Crawford Market', '9012345678'), # Spices & Oils
            ('supplier3', generate_password_hash('password123'), 'supplier', 'Meena Devi', 'Green Grocers', 'Sion Koliwada', '9554433221'), # Other Veggies/Fruits
            ('supplier4', generate_password_hash('password123'), 'supplier', 'Rajesh Gupta', 'Dairy Delights', 'Andheri East', '9667788990'), # Dairy & Butter
            ('supplier5', generate_password_hash('password123'), 'supplier', 'Kartik Singh', 'Pak N Serve', 'Lower Parel', '9778899001'), # Packing/Serving
            ('supplier6', generate_password_hash('password123'), 'supplier', 'Lata Rao', 'Sauce Master', 'Bandra West', '9112233445') # Sauces
        ]
        cursor.executemany(
            "INSERT OR IGNORE INTO users (username, password, role, name, shop_business_name, locality, contact_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
            users_data
        )
        print("Dummy users added/updated.")

        # Get the IDs of the dummy users (important for linking)
        user_ids = {}
        for row in cursor.execute("SELECT id, username FROM users").fetchall():
            user_ids[row['username']] = row['id']

        supplier1_id = user_ids['supplier1']
        supplier2_id = user_ids['supplier2']
        supplier3_id = user_ids['supplier3']
        supplier4_id = user_ids['supplier4']
        supplier5_id = user_ids['supplier5']
        supplier6_id = user_ids['supplier6']

        # 2. Add Dummy Products with more diverse categories
        products_data = [
            # Vegetables
            ('Potato', 'kg', 'Vegetables'), ('Onion', 'kg', 'Vegetables'), ('Tomato', 'kg', 'Vegetables'),
            ('Green Chilli', 'kg', 'Vegetables'), ('Coriander', 'bunch', 'Vegetables'),
            ('Cauliflower', 'kg', 'Vegetables'), ('Cabbage', 'kg', 'Vegetables'),
            ('Spinach', 'kg', 'Vegetables'), ('Brinjal', 'kg', 'Vegetables'),

            # Fruits
            ('Banana', 'dozen', 'Fruits'), ('Apple', 'kg', 'Fruits'), ('Orange', 'kg', 'Fruits'),

            # Sauces
            ('Tomato Ketchup', 'bottle', 'Sauces'), ('Chilli Sauce', 'bottle', 'Sauces'),
            ('Soy Sauce', 'bottle', 'Sauces'),

            # Spices
            ('Red Chilli Powder', 'kg', 'Spices'), ('Turmeric Powder', 'kg', 'Spices'),
            ('Cumin Seeds', 'kg', 'Spices'), ('Garam Masala', 'kg', 'Spices'),

            # Oil & Butter
            ('Cooking Oil', 'liter', 'Oil & Butter'), ('Ghee', 'kg', 'Oil & Butter'),
            ('Butter', 'kg', 'Oil & Butter'),

            # Packing Material
            ('Paper Plates', 'pack', 'Packing Material'), ('Disposable Cups', 'pack', 'Packing Material'),
            ('Food Containers', 'pack', 'Packing Material'), ('Napkins', 'pack', 'Packing Material'),

            # Serving Material (could overlap with packing but distinct in context)
            ('Serving Spoons', 'piece', 'Serving Material'), ('Tray', 'piece', 'Serving Material')
        ]
        cursor.executemany("INSERT OR IGNORE INTO products (name, unit, category) VALUES (?, ?, ?)", products_data)
        print("Dummy products added/updated.")

        # Get product IDs for linking
        product_ids = {}
        for row in cursor.execute("SELECT id, name FROM products").fetchall():
            product_ids[row['name']] = row['id']

        # 3. Add Dummy Supplier Products (prices for the dummy suppliers)
        supplier_products_data = [
            # Fresh Veggies Co. (supplier1)
            (supplier1_id, product_ids['Potato'], 25.0, 100),
            (supplier1_id, product_ids['Onion'], 30.0, 150),
            (supplier1_id, product_ids['Tomato'], 40.0, 80),
            (supplier1_id, product_ids['Green Chilli'], 60.0, 50),
            (supplier1_id, product_ids['Coriander'], 10.0, 200),
            (supplier1_id, product_ids['Spinach'], 25.0, 70),

            # Spice World (supplier2)
            (supplier2_id, product_ids['Cooking Oil'], 120.0, 50),
            (supplier2_id, product_ids['Red Chilli Powder'], 250.0, 30),
            (supplier2_id, product_ids['Turmeric Powder'], 180.0, 40),
            (supplier2_id, product_ids['Cumin Seeds'], 90.0, 60),
            (supplier2_id, product_ids['Garam Masala'], 300.0, 25),

            # Green Grocers (supplier3)
            (supplier3_id, product_ids['Cauliflower'], 35.0, 90),
            (supplier3_id, product_ids['Cabbage'], 20.0, 110),
            (supplier3_id, product_ids['Banana'], 45.0, 10), # Dozen
            (supplier3_id, product_ids['Apple'], 150.0, 30),
            (supplier3_id, product_ids['Orange'], 80.0, 50),
            (supplier3_id, product_ids['Brinjal'], 30.0, 60),


            # Dairy Delights (supplier4)
            (supplier4_id, product_ids['Milk'], 65.0, 200), # Liter
            (supplier4_id, product_ids['Paneer'], 320.0, 40),
            (supplier4_id, product_ids['Ghee'], 550.0, 20),
            (supplier4_id, product_ids['Butter'], 480.0, 50),

            # Pak N Serve (supplier5)
            (supplier5_id, product_ids['Paper Plates'], 80.0, 50), # Pack
            (supplier5_id, product_ids['Disposable Cups'], 60.0, 70),
            (supplier5_id, product_ids['Food Containers'], 150.0, 30),
            (supplier5_id, product_ids['Napkins'], 40.0, 100),
            (supplier5_id, product_ids['Serving Spoons'], 120.0, 20),

            # Sauce Master (supplier6)
            (supplier6_id, product_ids['Tomato Ketchup'], 90.0, 60),
            (supplier6_id, product_ids['Chilli Sauce'], 85.0, 55),
            (supplier6_id, product_ids['Soy Sauce'], 75.0, 45)
        ]
        for sp_data in supplier_products_data:
            try:
                cursor.execute(
                    "INSERT INTO supplier_products (supplier_id, product_id, price_per_unit, stock) VALUES (?, ?, ?, ?)",
                    sp_data
                )
            except sqlite3.IntegrityError:
                # This catches if a (supplier_id, product_id) pair already exists
                print(f"Skipping duplicate supplier_product entry: {sp_data}")
                pass

        print("Dummy supplier products added/updated.")

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"An error occurred during population: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    init_db_schema() # Ensure the schema is fresh
    populate_initial_data() # Then populate with data