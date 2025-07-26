from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_for_hackathon' # IMPORTANT: Keep this same for hackathon purposes

DATABASE = os.path.join(app.root_path, 'database.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open(os.path.join(app.root_path, 'schema.sql'), 'r') as f:
            db.executescript(f.read())
        db.commit()
        print("Database initialized successfully.")

app.teardown_appcontext(close_db)

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()

@app.route('/')
def index():
    if g.user:
        if g.user['role'] == 'vendor':
            return redirect(url_for('vendor_dashboard'))
        elif g.user['role'] == 'supplier':
            return redirect(url_for('supplier_dashboard'))
    return render_template('index.html')

@app.route('/register', methods=('GET', 'POST'))
def register():
    # ... (Keep this code exactly as before) ...
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        name = request.form.get('name')
        shop_business_name = request.form.get('shop_business_name')
        locality = request.form.get('locality')
        contact_number = request.form.get('contact_number')

        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif role not in ['vendor', 'supplier']:
            error = 'Invalid role selected.'

        db = get_db()
        if error is None:
            try:
                hashed_password = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (username, password, role, name, shop_business_name, locality, contact_number) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (username, hashed_password, role, name, shop_business_name, locality, contact_number)
                )
                db.commit()
            except sqlite3.IntegrityError:
                error = f"User '{username}' is already registered."
            else:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))

        flash(error, 'danger')
    return render_template('register.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    # ... (Keep this code exactly as before) ...
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['user_role'] = user['role']
            flash('Logged in successfully!', 'success')
            if user['role'] == 'vendor':
                return redirect(url_for('vendor_dashboard'))
            elif user['role'] == 'supplier':
                return redirect(url_for('supplier_dashboard'))
        flash(error, 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    # ... (Keep this code exactly as before) ...
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/vendor_dashboard')
def vendor_dashboard():
    if not g.user or g.user['role'] != 'vendor':
        flash('Please log in as a vendor to access this page.', 'warning')
        return redirect(url_for('login'))

    db = get_db()
    # Fetch all unique categories
    categories = db.execute("SELECT DISTINCT category FROM products ORDER BY category").fetchall()
    # Fetch all suppliers
    suppliers = db.execute("SELECT id, name, shop_business_name FROM users WHERE role = 'supplier' ORDER BY shop_business_name").fetchall()
    # Fetch all supplier products (we'll filter them on the frontend for now)
    all_supplier_products = db.execute(
        """
        SELECT
            sp.id AS supplier_product_id,
            u.id AS supplier_id,
            u.name AS supplier_contact_name,
            u.shop_business_name,
            p.id AS product_id,
            p.name AS product_name,
            p.unit,
            p.category, -- Include category for filtering
            sp.price_per_unit,
            sp.stock
        FROM supplier_products sp
        JOIN users u ON sp.supplier_id = u.id
        JOIN products p ON sp.product_id = p.id
        WHERE u.role = 'supplier'
        ORDER BY u.shop_business_name, p.name
        """
    ).fetchall()

    return render_template(
        'vendor_dashboard.html',
        categories=categories,
        suppliers=suppliers,
        all_supplier_products=all_supplier_products
    )

@app.route('/supplier_dashboard')
def supplier_dashboard():
    # ... (Keep this code exactly as before) ...
    if not g.user or g.user['role'] != 'supplier':
        flash('Please log in as a supplier to access this page.', 'warning')
        return redirect(url_for('login'))

    db = get_db()
    incoming_orders = db.execute(
        """
        SELECT
            o.id AS order_id,
            o.order_date,
            o.status,
            o.total_amount,
            v.shop_business_name AS vendor_name,
            GROUP_CONCAT(p.name || ' (' || oi.quantity || ' ' || p.unit || ')', ' ||| ') AS items_summary
        FROM orders o
        JOIN users v ON o.vendor_id = v.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.supplier_id = ?
        GROUP BY o.id
        ORDER BY o.order_date DESC
        """, (g.user['id'],)
    ).fetchall()

    return render_template('supplier_dashboard.html', incoming_orders=incoming_orders)

@app.route('/my_orders')
def my_orders():
    # ... (Keep this code exactly as before) ...
    if not g.user or g.user['role'] != 'vendor':
        flash('Please log in as a vendor to access this page.', 'warning')
        return redirect(url_for('login'))

    db = get_db()
    orders = db.execute(
        """
        SELECT
            o.id AS order_id,
            o.order_date,
            o.status,
            o.total_amount,
            s.shop_business_name AS supplier_name,
            GROUP_CONCAT(p.name || ' (' || oi.quantity || ' ' || p.unit || ' @Rs.' || oi.price_at_order || ')', ' ||| ') AS items_summary
        FROM orders o
        JOIN users s ON o.supplier_id = s.id
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE o.vendor_id = ?
        GROUP BY o.id
        ORDER BY o.order_date DESC
        """, (g.user['id'],)
    ).fetchall()

    return render_template('my_orders.html', orders=orders)

@app.route('/api/place_order', methods=['POST'])
def api_place_order():
    # ... (Keep this code exactly as before) ...
    if not g.user or g.user['role'] != 'vendor':
        return jsonify({'success': False, 'message': 'Unauthorized or not a vendor'}), 401

    vendor_id = g.user['id']
    order_items_data = request.json # Expecting a list of item objects

    if not order_items_data:
        return jsonify({'success': False, 'message': 'No order data provided'}), 400

    db = get_db()
    try:
        cursor = db.cursor()

        # For simplicity, assume all items in one POST are for one supplier for now
        # You might enhance this to handle multiple suppliers in one cart if needed
        if not order_items_data:
            return jsonify({'success': False, 'message': 'Order items list is empty.'}), 400

        # Get the supplier_id from the first item (assuming single supplier order)
        # This is CRITICAL: Ensure your frontend JS sends a valid supplier_id with each item
        supplier_id = order_items_data[0]['supplier_id']

        total_amount = 0

        # Create the main order entry
        cursor.execute(
            "INSERT INTO orders (vendor_id, supplier_id, status, total_amount) VALUES (?, ?, ?, ?)",
            (vendor_id, supplier_id, 'Pending', 0.0)
        )
        order_id = cursor.lastrowid

        # Add individual order items
        for item in order_items_data:
            product_id = item['product_id']
            quantity = item['quantity']
            price_at_order = item['price_per_unit']

            item_total = quantity * price_at_order
            total_amount += item_total

            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price_at_order) VALUES (?, ?, ?, ?)",
                (order_id, product_id, quantity, price_at_order)
            )

        # Update total_amount in the orders table
        cursor.execute(
            "UPDATE orders SET total_amount = ? WHERE id = ?",
            (total_amount, order_id)
        )
        db.commit()
        return jsonify({'success': True, 'message': 'Order placed successfully!', 'order_id': order_id})

    except Exception as e:
        db.rollback()
        print(f"Error placing order: {e}") # For debugging
        return jsonify({'success': False, 'message': f'Error placing order: {str(e)}'}), 500


if __name__ == '__main__':
    # init_db() # Uncomment and run once if you want to initialize without dummy data
    app.run(debug=True)