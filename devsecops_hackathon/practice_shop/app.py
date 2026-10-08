from flask import Flask, request, jsonify
from functools import wraps
import os

app = Flask(__name__)

# FIX 1: API key loaded from environment variable (not hardcoded)
PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY", "fallback_key_do_not_use_in_prod")

# --- Mock Database ---
CATALOG = {
    "1": {"name": "Hacker Laptop Pro", "price": 1000.00},
    "2": {"name": "Mechanical Keyboard (Cherry MX)", "price": 150.00},
    "3": {"name": "Flipper Zero (PenTest Tool)", "price": 169.00},
    "4": {"name": "Raspberry Pi 5 Server", "price": 80.00},
    "5": {"name": "Hak5 WiFi Pineapple", "price": 120.00},
    "6": {"name": "Noise Cancelling Headphones", "price": 250.00}
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

# FIX 2: Auth decorator to protect routes
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/products', methods=['GET'])
def get_products():
    return jsonify(CATALOG)

# FIX 2: Added @require_auth
# FIX 3: Price is looked up from CATALOG, not from user input
@app.route('/api/checkout', methods=['POST'])
@require_auth
def checkout():
    data = request.json
    user_id = data.get("user_id")
    product_id = str(data.get("product_id"))
    
    if product_id not in CATALOG:
        return jsonify({"error": "Product not found"}), 404
        
    product_name = CATALOG[product_id]["name"]
    safe_price = CATALOG[product_id]["price"]
    
    if user_id not in ORDERS:
        ORDERS[user_id] = []
    ORDERS[user_id].append({"id": 999, "item": product_name, "paid": safe_price})
    
    return jsonify({
        "status": "success", 
        "message": f"Securely purchased {product_name} for ${safe_price}"
    })

# FIX 2: Added @require_auth
# FIX 4: IDOR ownership check added
@app.route('/api/orders/<user_id>', methods=['GET'])
@require_auth
def get_orders(user_id):
    current_user = ""
    auth_header = request.headers.get("Authorization", "")
    if " " in auth_header:
        current_user = auth_header.split(" ")[1]
    
    if current_user != user_id and current_user != "admin_99":
        return jsonify({"error": "Forbidden. You cannot view other users' orders."}), 403
        
    user_orders = ORDERS.get(user_id, [])
    return jsonify({"user_id": user_id, "orders": user_orders})

# FIX 2: Added @require_auth
# FIX 5: Removed leaked API key and credit card from response
@app.route('/api/admin/stats', methods=['GET'])
@require_auth
def admin_stats():
    total = sum(order["paid"] for user_orders in ORDERS.values() for order in user_orders)
    return jsonify({
        "total_revenue": total, 
        "active_users": len(ORDERS.keys())
    })

if __name__ == '__main__':
    app.run(port=8001, debug=True)
