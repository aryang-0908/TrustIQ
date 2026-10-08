from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import re
import json
import time
import jwt
from datetime import datetime
from collections import defaultdict
from colorama import init, Fore, Style
import sys

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

init(autoreset=True)
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for the frontend

# ==========================================
# CONFIGURATION
# ==========================================
TARGET_URL = "http://127.0.0.1:8001"
JWT_SECRET = "TrustIQ_hackathon_secret_2026"
RATE_LIMIT_MAX = 10           # Max requests per window
RATE_LIMIT_WINDOW = 60        # Window in seconds
AUTO_BAN_THRESHOLD = 3        # Ban IP after this many blocked attacks
AUDIT_LOG_FILE = "security_log.json"
DISCORD_WEBHOOK_URL = None     # Set your Discord webhook URL here to enable alerts

# Product catalog (trusted server-side copy)
VALID_PRICES = {"1": 1000.00, "2": 150.00, "3": 169.00, "4": 80.00, "5": 120.00, "6": 250.00}

# ==========================================
# IN-MEMORY TRACKING
# ==========================================
rate_limit_tracker = defaultdict(list)      # IP -> [timestamp, timestamp, ...]
attack_counter = defaultdict(int)           # IP -> count of blocked attacks
ip_blocklist = set()                        # Set of banned IPs
security_stats = {
    "total_blocked": 0,
    "auth_failures": 0,
    "idor_attempts": 0,
    "price_tampering": 0,
    "sql_injection": 0,
    "xss_attempts": 0,
    "rate_limited": 0,
    "dlp_scrubbed": 0,
    "ip_bans": 0,
    "total_forwarded": 0,
    "recent_attacks": []
}

# ==========================================
# DLP (Data Loss Prevention) Patterns
# ==========================================
DLP_PATTERNS = [
    (re.compile(r'sk_live_[a-zA-Z0-9]+'), "[REDACTED_API_KEY]", "API Key"),
    (re.compile(r'sk_test_[a-zA-Z0-9]+'), "[REDACTED_TEST_KEY]", "Test API Key"),
    (re.compile(r'AKIA[0-9A-Z]{16}'), "[REDACTED_AWS_KEY]", "AWS Key"),
    (re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b'), "[REDACTED_CREDIT_CARD]", "Credit Card"),
    (re.compile(r'[a-zA-Z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook)\.[a-zA-Z]{2,}'), "[REDACTED_EMAIL]", "Email Address"),
    (re.compile(r'(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)'), "[REDACTED_PHONE]", "Phone Number"),
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), "[REDACTED_SSN]", "SSN"),
]

# SQL Injection patterns
SQL_PATTERNS = [
    re.compile(r"(\b(union|select|insert|update|delete|drop|alter|exec|execute)\b.*(\b(from|into|where|table|database)\b))", re.IGNORECASE),
    re.compile(r"('.*(--))", re.IGNORECASE),
    re.compile(r"('\s*(or|and)\s*'?\d*'?\s*=\s*'?\d*)", re.IGNORECASE),
    re.compile(r"(;\s*(drop|alter|delete|update|insert)\s)", re.IGNORECASE),
]

# XSS patterns
XSS_PATTERNS = [
    re.compile(r'<\s*script', re.IGNORECASE),
    re.compile(r'javascript\s*:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
    re.compile(r'<\s*iframe', re.IGNORECASE),
    re.compile(r'<\s*img\s+.*onerror', re.IGNORECASE),
]

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def get_client_ip():
    return request.headers.get('X-Forwarded-For', request.remote_addr)

def log_attack(ip, attack_type, details, path):
    """Save blocked attack to audit log file and in-memory stats."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "ip": ip,
        "attack_type": attack_type,
        "path": path,
        "details": details,
        "method": request.method
    }
    
    # Write to file
    try:
        logs = []
        try:
            with open(AUDIT_LOG_FILE, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        logs.append(entry)
        with open(AUDIT_LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)
    except Exception as e:
        print(f"{Fore.YELLOW}[LOG WARNING] Could not write audit log: {e}")
    
    # Update in-memory stats
    security_stats["total_blocked"] += 1
    security_stats["recent_attacks"].append(entry)
    if len(security_stats["recent_attacks"]) > 50:
        security_stats["recent_attacks"] = security_stats["recent_attacks"][-50:]
    
    # Track attacks per IP for auto-ban
    attack_counter[ip] += 1
    if attack_counter[ip] >= AUTO_BAN_THRESHOLD and ip not in ip_blocklist:
        ip_blocklist.add(ip)
        security_stats["ip_bans"] += 1
        print(f"{Fore.RED}{Style.BRIGHT}[AUTO-BAN] IP {ip} has been permanently banned after {AUTO_BAN_THRESHOLD} attacks!")
    
    # Send Discord webhook alert (if configured)
    send_webhook_alert(entry)

def send_webhook_alert(entry):
    """Send an alert to Discord/Slack webhook."""
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        payload = {
            "content": f"**[TrustIQ Alert]** {entry['attack_type']} blocked!\n"
                       f"IP: `{entry['ip']}` | Path: `{entry['path']}`\n"
                       f"Details: {entry['details']}\n"
                       f"Time: {entry['timestamp']}"
        }
        requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=3)
    except:
        pass

def check_rate_limit(ip):
    """Returns True if the IP has exceeded the rate limit."""
    now = time.time()
    # Clean old entries
    rate_limit_tracker[ip] = [t for t in rate_limit_tracker[ip] if now - t < RATE_LIMIT_WINDOW]
    # Check limit
    if len(rate_limit_tracker[ip]) >= RATE_LIMIT_MAX:
        return True
    rate_limit_tracker[ip].append(now)
    return False

def check_sql_injection(text):
    """Returns True if SQL injection pattern is found."""
    if not text:
        return False
    for pattern in SQL_PATTERNS:
        if pattern.search(text):
            return True
    return False

def check_xss(text):
    """Returns True if XSS pattern is found."""
    if not text:
        return False
    for pattern in XSS_PATTERNS:
        if pattern.search(text):
            return True
    return False

def scan_request_for_injection(req):
    """Scan all parts of the request for SQL injection and XSS."""
    # Check URL path and query string
    full_url = req.url
    if check_sql_injection(full_url):
        return "SQL_INJECTION", "Malicious SQL detected in URL"
    if check_xss(full_url):
        return "XSS", "Malicious script detected in URL"
    
    # Check request body
    body = req.get_data(as_text=True)
    if body:
        if check_sql_injection(body):
            return "SQL_INJECTION", "Malicious SQL detected in request body"
        if check_xss(body):
            return "XSS", "Malicious script detected in request body"
    
    # Check all headers (except standard ones)
    for key, value in req.headers:
        if key.lower() not in ('host', 'content-type', 'content-length', 'user-agent', 'accept', 'authorization', 'connection'):
            if check_sql_injection(value) or check_xss(value):
                return "INJECTION", f"Malicious payload detected in header: {key}"
    
    return None, None

def validate_jwt_token(token):
    """Validate a JWT token and return the user_id, or None if invalid."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ==========================================
# SECURITY DASHBOARD API
# ==========================================
@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Returns live security statistics."""
    stats = dict(security_stats)
    stats["banned_ips"] = list(ip_blocklist)
    stats["active_rate_limits"] = len(rate_limit_tracker)
    return jsonify(stats)

@app.route('/dashboard/logs', methods=['GET'])
def dashboard_logs():
    """Returns the full audit log."""
    try:
        with open(AUDIT_LOG_FILE, 'r') as f:
            logs = json.load(f)
        return jsonify(logs)
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify([])

@app.route('/dashboard/generate-token', methods=['POST'])
def generate_token():
    """Helper endpoint to generate JWT tokens for testing."""
    data = request.json
    user_id = data.get("user_id", "test_user")
    token = jwt.encode({"user_id": user_id, "iat": time.time()}, JWT_SECRET, algorithm="HS256")
    return jsonify({"token": token, "user_id": user_id})

@app.route('/dashboard/scan', methods=['POST'])
def scan_code():
    """Endpoint for the frontend Oracle Chatbox to scan code snippets."""
    code = request.json.get("code", "")
    if not code:
        return jsonify({"vulnerabilities": []})
        
    lines = code.split('\n')
    findings = []
    
    # We will reuse the DLP/SQL/XSS patterns we already have loaded in the proxy
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Check for Secrets / PII (Using DLP Patterns)
        for pattern, replacement, desc in DLP_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "line": line_num,
                    "issue": f"Exposed {desc}",
                    "fix": "Move to environment variables or use a secure vault."
                })
                
        # Check for SQL Injection
        for pattern in SQL_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "line": line_num,
                    "issue": "Potential SQL Injection",
                    "fix": "Use parameterized queries or an ORM."
                })
                
        # Check for XSS
        for pattern in XSS_PATTERNS:
            if pattern.search(line):
                findings.append({
                    "line": line_num,
                    "issue": "Potential Cross-Site Scripting (XSS)",
                    "fix": "Sanitize user input before rendering it in the DOM."
                })
                
        # Generic Secret Check (fallback)
        if "password" in line.lower() or "api_key" in line.lower() or "secret" in line.lower():
            if "=" in line or ":" in line:
                # Prevent duplicates
                if not any(f["line"] == line_num and "Exposed" in f["issue"] for f in findings):
                    findings.append({
                        "line": line_num,
                        "issue": "Hardcoded Credential/Secret",
                        "fix": "Use os.getenv() or a secret manager."
                    })
                    
    return jsonify({"vulnerabilities": findings})

# ==========================================
# MAIN PROXY ROUTE
# ==========================================
@app.route('/api/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/api/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    path = f"api/{path}" if path else "api/"
    full_url = f"{TARGET_URL}/{path}"
    client_ip = get_client_ip()
    headers = {key: value for (key, value) in request.headers if key != 'Host'}
    
    print(f"\n{Fore.CYAN}[PROXY] {request.method} /{path} from {client_ip}")
    
    # ==========================================
    # RULE 0: IP BLOCKLIST CHECK
    # ==========================================
    if client_ip in ip_blocklist:
        print(f"{Fore.RED}[BANNED] IP {client_ip} is permanently banned.")
        return jsonify({"error": "TrustIQ: Your IP has been permanently banned."}), 403

    # ==========================================
    # RULE 1: RATE LIMITING
    # ==========================================
    if check_rate_limit(client_ip):
        security_stats["rate_limited"] += 1
        log_attack(client_ip, "RATE_LIMIT", f"Exceeded {RATE_LIMIT_MAX} requests in {RATE_LIMIT_WINDOW}s", path)
        print(f"{Fore.RED}[BLOCKED] Rate limit exceeded for {client_ip}")
        return jsonify({"error": "TrustIQ: Rate limit exceeded. Slow down."}), 429

    # ==========================================
    # RULE 2: SQL INJECTION & XSS DETECTION
    # ==========================================
    attack_type, attack_detail = scan_request_for_injection(request)
    if attack_type:
        stat_key = "sql_injection" if "SQL" in attack_type else "xss_attempts"
        security_stats[stat_key] += 1
        log_attack(client_ip, attack_type, attack_detail, path)
        print(f"{Fore.RED}[BLOCKED] {attack_type}: {attack_detail}")
        return jsonify({"error": f"TrustIQ: {attack_type} detected and blocked."}), 400

    # ==========================================
    # RULE 3: AUTH ENFORCEMENT
    # ==========================================
    protected_routes = ['api/checkout', 'api/admin', 'api/orders']
    is_protected = any(path.startswith(route) for route in protected_routes)
    auth_header = request.headers.get("Authorization")
    
    if is_protected and not auth_header:
        security_stats["auth_failures"] += 1
        log_attack(client_ip, "AUTH_FAILURE", "Missing Authorization header", path)
        print(f"{Fore.RED}[BLOCKED] Missing Authorization header on protected route.")
        return jsonify({"error": "TrustIQ: Unauthorized. Missing Token."}), 401
        
    # Parse the token (supports both simple Bearer tokens and JWT)
    current_user = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        # Try JWT first, fall back to simple token
        current_user = validate_jwt_token(token)
        if not current_user:
            current_user = token  # Fallback: treat token as plain user ID
        
    # ==========================================
    # RULE 4: IDOR (OWNERSHIP VALIDATION)
    # ==========================================
    if path.startswith('api/orders/'):
        requested_user_id = path.split('/')[-1]
        if current_user != requested_user_id and current_user != "admin_99":
            security_stats["idor_attempts"] += 1
            log_attack(client_ip, "IDOR", f"User '{current_user}' tried to access '{requested_user_id}'s data", path)
            print(f"{Fore.RED}[BLOCKED] IDOR Attempt. User '{current_user}' tried to access '{requested_user_id}'s data.")
            return jsonify({"error": "TrustIQ: Forbidden. You do not own this resource."}), 403

    # ==========================================
    # RULE 5: PRICE TAMPERING
    # ==========================================
    if path.startswith('api/checkout') and request.method == 'POST':
        data = request.json
        if data:
            product_id = str(data.get("product_id"))
            provided_price = float(data.get("price", 0))
            if product_id in VALID_PRICES and provided_price != VALID_PRICES[product_id]:
                security_stats["price_tampering"] += 1
                log_attack(client_ip, "PRICE_TAMPERING", f"Client sent ${provided_price}, actual is ${VALID_PRICES[product_id]}", path)
                print(f"{Fore.RED}[BLOCKED] Price Tampering! Client sent ${provided_price}, actual is ${VALID_PRICES[product_id]}.")
                return jsonify({"error": "TrustIQ: Payload validation failed. Malicious price detected."}), 400

    # ==========================================
    # ALL CHECKS PASSED: FORWARD THE REQUEST
    # ==========================================
    print(f"{Fore.GREEN}[PASSED] Request looks safe. Forwarding to backend...")
    security_stats["total_forwarded"] += 1
    
    resp = requests.request(
        method=request.method, url=full_url, headers=headers,
        data=request.get_data(), cookies=request.cookies, allow_redirects=False
    )
    
    # ==========================================
    # RULE 6: DLP (DATA LOSS PREVENTION) - EGRESS FILTERING
    # ==========================================
    response_text = resp.text
    dlp_triggered = False
    dlp_types = []
    
    content_type = resp.headers.get('Content-Type', '')
    if 'application/json' in content_type or 'text/' in content_type:
        for pattern, replacement, data_type in DLP_PATTERNS:
            if pattern.search(response_text):
                dlp_triggered = True
                dlp_types.append(data_type)
                response_text = pattern.sub(replacement, response_text)
                
    if dlp_triggered:
        security_stats["dlp_scrubbed"] += 1
        types_str = ", ".join(dlp_types)
        log_attack(client_ip, "DLP_LEAK", f"Scrubbed outbound data: {types_str}", path)
        print(f"{Fore.RED}{Style.BRIGHT}[DLP ALERT] Sensitive data detected in outbound response: {types_str}")
        print(f"{Fore.RED}{Style.BRIGHT}[DLP ALERT] Data scrubbed before reaching the client.")
        content_to_return = response_text.encode('utf-8')
    else:
        content_to_return = resp.content

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    response_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
                        
    return Response(content_to_return, resp.status_code, response_headers)

if __name__ == '__main__':
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}=====================================================")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}  TrustIQ Zero-Trust Proxy v2.0")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}  Features: Auth | IDOR | Price | SQLi | XSS | DLP")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}            Rate Limit | Auto-Ban | Audit Log")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}  Dashboard: http://127.0.0.1:8000/dashboard")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}  Protecting: {TARGET_URL}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}=====================================================\n")
    app.run(port=8000, debug=True, use_reloader=False)
