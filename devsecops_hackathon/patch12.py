import re

with open("proxy/proxy.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find Rule 5 and add header checking before it
rule_5_marker = "# RULE 5: GENERIC PAYLOAD TAMPERING & PRIVILEGE ESCALATION"

header_check = """    # ==========================================
    # RULE 4.5: MALICIOUS HEADER DETECTION
    # ==========================================
    restricted_headers = ['is_admin', 'role', 'permissions', 'x-forwarded-user', 'x-admin']
    for req_header in request.headers.keys():
        if req_header.lower() in restricted_headers:
            security_stats["idor_attempts"] += 1
            log_attack(client_ip, "PRIVILEGE_ESCALATION", f"Attempted to inject restricted header: {req_header}", path)
            print(f"{Fore.RED}[BLOCKED] Privilege Escalation Attempt via Header: {req_header}.")
            return jsonify({"error": f"TrustIQ: Privilege escalation attempt via {req_header} blocked."}), 403

    # ==========================================
    # RULE 5: GENERIC PAYLOAD TAMPERING & PRIVILEGE ESCALATION"""

if rule_5_marker in content:
    content = content.replace(rule_5_marker, header_check)
    with open("proxy/proxy.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched proxy.py to block malicious headers.")
else:
    print("Could not find RULE 5 marker.")

