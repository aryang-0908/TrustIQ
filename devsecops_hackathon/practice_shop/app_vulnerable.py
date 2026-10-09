from flask import Flask, request, jsonify

app = Flask(__name__)

# FLAW 1: Hardcoded Secrets (multiple types)
PAYMENT_API_KEY = "sk_fake_93a1f8b83c7d6e5f4a3b2c1d0e9f8a7b"
AWS_ACCESS_KEY = "MOCK1234567890ABCDEF"
DB_PASSWORD = "super_secret_database_password_123"

# FLAW 6: PII in source code
ADMIN_EMAIL = "admin@gmail.com"
SUPPORT_PHONE = "+91-9876543210"

# --- Mock Database ---
CATALOG = {
    "1": {"name": "Nova Pro Wireless Headphones", "price": 24999.00},
    "2": {"name": "Obsidian Mechanical Keyboard", "price": 12499.00},
    "3": {"name": "Nova Watch Series X", "price": 34999.00},
    "4": {"name": "Acoustic Tower Speaker", "price": 45000.00},
    "5": {"name": "Ergo Desk Setup", "price": 8999.00},
    "6": {"name": "Smart Display Hub", "price": 15999.00}
}

USERS = {
    "user_1": {"name": "Alice", "email": "alice@gmail.com", "phone": "9876543210", "ssn": "123-45-6789"},
    "user_2": {"name": "Bob", "email": "bob@yahoo.com", "phone": "8765432109"},
    "user_3": {"name": "Charlie", "email": "charlie@hotmail.com", "phone": "7654321098"},
    "admin_99": {"name": "Admin", "email": "admin@company.com", "phone": "9999999999"}
}

ORDERS = {
    "user_1": [
        {"id": 101, "item": "Mechanical Keyboard (Cherry MX)", "paid": 150.00},
        {"id": 102, "item": "Raspberry Pi 5 Server", "paid": 80.00}
    ],
    "user_2": [
        {"id": 103, "item": "Hacker Laptop Pro", "paid": 1000.00}
    ],
    "user_3": [
        {"id": 104, "item": "Flipper Zero (PenTest Tool)", "paid": 169.00},
        {"id": 105, "item": "Hak5 WiFi Pineapple", "paid": 120.00}
    ],
    "admin_99": [
        {"id": 999, "item": "Top Secret Server Infrastructure", "paid": 50000.00}
    ]
}

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(CATALOG)

# FLAW 2: Missing Auth
# FLAW 3: Price Tampering
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.json
    user_id = data.get("user_id")
    product_id = str(data.get("product_id"))
    user_provided_price = data.get("price")
    
    if product_id not in CATALOG:
        return jsonify({"error": "Product not found"}), 404
        
    product_name = CATALOG[product_id]["name"]
    print(f"[SYSTEM] Processing payment of ${user_provided_price} via {PAYMENT_API_KEY}")
    
    if user_id not in ORDERS:
        ORDERS[user_id] = []
    ORDERS[user_id].append({"id": 999, "item": product_name, "paid": user_provided_price})
    
    return jsonify({
        "status": "success", 
        "message": f"Successfully purchased {product_name} for ${user_provided_price}"
    })

# FLAW 4: IDOR
@app.route('/api/orders/<user_id>', methods=['GET'])
def get_orders(user_id):
    user_orders = ORDERS.get(user_id, [])
    user_info = USERS.get(user_id, {})
    return jsonify({
        "user_id": user_id,
        "user_info": user_info,
        "orders": user_orders
    })

# FLAW 5: Data Leak (API key, credit card, PII in response)
@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    total = sum(order["paid"] for user_orders in ORDERS.values() for order in user_orders)
    return jsonify({
        "total_revenue": total, 
        "active_users": len(ORDERS.keys()),
        "system_payment_key": PAYMENT_API_KEY,
        "recent_credit_card": "4111-2222-3333-4444",
        "admin_email": ADMIN_EMAIL,
        "support_phone": SUPPORT_PHONE
    })

# FLAW 7: SQL Injection (simulated)
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    # Vulnerable: directly inserting user input into a query string
    sql = f"SELECT * FROM products WHERE name LIKE '%{query}%'"
    print(f"[DB] Executing: {sql}")
    
    # Simulate search results
    results = []
    for pid, product in CATALOG.items():
        if query.lower() in product["name"].lower():
            results.append(product)
    return jsonify({"query": query, "sql_executed": sql, "results": results})

# FLAW 8: XSS (simulated - stores and returns unescaped user input)
REVIEWS = []
@app.route('/api/reviews', methods=['GET', 'POST'])
def reviews():
    if request.method == 'POST':
        data = request.json
        review_text = data.get("review", "")
        # Vulnerable: stores raw user input without sanitization
        REVIEWS.append({"user": data.get("user", "anonymous"), "review": review_text})
        return jsonify({"status": "Review added", "review": review_text})
    return jsonify({"reviews": REVIEWS})

@app.route('/api/leak_key', methods=['GET'])
def leak_key():
    # Intentionally leaks a fake live API key
    return jsonify({"status": "success", "api_key": "sk_live_abc123DEF456ghi789"})

if __name__ == '__main__':
    app.run(port=8001, debug=True)
