import sys
import re
import os
import json
import argparse
import math
from datetime import datetime
from colorama import init, Fore, Style

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

init(autoreset=True)

# ==========================================
# DETECTION RULES
# ==========================================

# Rule 1: Hardcoded Secrets (API keys, passwords, tokens)
SECRET_PATTERNS = [
    (re.compile(r'sk_(live|test|fake)_[a-zA-Z0-9]{10,}'), "Hardcoded Stripe API key"),
    (re.compile(r'(AKIA|MOCK)[0-9A-Z]{16}'), "Hardcoded AWS Access Key"),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), "Hardcoded GitHub Personal Token"),
    (re.compile(r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{4,}["\']'), "Hardcoded password"),
    (re.compile(r'(?i)(api_key|apikey|secret_key|secret)\s*=\s*["\'][^"\']{8,}["\']'), "Hardcoded secret/API key"),
]

# Rule 2: Price Tampering
PRICE_TAMPER_PATTERNS = [
    re.compile(r'request\.json\.get\([\'"]price[\'"]\)'),
    re.compile(r'request\.form\.get\([\'"]price[\'"]\)'),
    re.compile(r'request\.args\.get\([\'"]price[\'"]\)'),
]

# Rule 3: SQL Injection (unsafe string formatting in queries)
SQL_INJECTION_PATTERNS = [
    (re.compile(r'f["\'].*(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER).*\{.*\}.*["\']', re.IGNORECASE), "SQL injection via f-string"),
    (re.compile(r'(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER).*%s', re.IGNORECASE), "SQL injection via %s formatting"),
    (re.compile(r'(?:SELECT|INSERT|UPDATE|DELETE|DROP|ALTER).*\+\s*(?:request|user_input|data)', re.IGNORECASE), "SQL injection via string concatenation"),
    (re.compile(r'\.execute\(\s*f["\']', re.IGNORECASE), "SQL injection in .execute() with f-string"),
    (re.compile(r'\.execute\(.*\+', re.IGNORECASE), "SQL injection in .execute() with concatenation"),
]

# Rule 4: XSS Detection (rendering user input without escaping)
XSS_PATTERNS = [
    (re.compile(r'innerHTML\s*='), "Potential XSS via innerHTML assignment"),
    (re.compile(r'document\.write\('), "Potential XSS via document.write"),
    (re.compile(r'\|\s*safe'), "Potential XSS via Jinja2 |safe filter"),
    (re.compile(r'Markup\(.*request'), "Potential XSS via Flask Markup with user input"),
]

# Rule 5: PII Detection (emails, phone numbers in source code)
PII_PATTERNS = [
    (re.compile(r'[a-zA-Z0-9._%+-]+@(?:gmail|yahoo|hotmail|outlook)\.[a-zA-Z]{2,}'), "Hardcoded email address (PII)"),
    (re.compile(r'(?<!\d)(?:\+91[-\s]?)?[6-9]\d{9}(?!\d)'), "Hardcoded Indian phone number (PII)"),
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), "Hardcoded SSN pattern (PII)"),
]

# Rule 6: Entropy Check for generic high-entropy strings (possible secrets)
def shannon_entropy(data):
    if not data:
        return 0
    entropy = 0
    for x in set(data):
        p_x = data.count(x) / len(data)
        if p_x > 0:
            entropy -= p_x * math.log2(p_x)
    return entropy

ENTROPY_REGEX = re.compile(r'["\'][A-Za-z0-9+/=_-]{20,}["\']')

# ==========================================
# DEPENDENCY SCANNER
# ==========================================
KNOWN_VULNERABLE_PACKAGES = {
    "flask": {"vulnerable_below": "2.3.0", "cve": "CVE-2023-30861", "severity": "HIGH"},
    "django": {"vulnerable_below": "4.2.0", "cve": "CVE-2023-31047", "severity": "HIGH"},
    "requests": {"vulnerable_below": "2.31.0", "cve": "CVE-2023-32681", "severity": "MEDIUM"},
    "werkzeug": {"vulnerable_below": "2.3.3", "cve": "CVE-2023-25577", "severity": "HIGH"},
    "jinja2": {"vulnerable_below": "3.1.3", "cve": "CVE-2024-22195", "severity": "MEDIUM"},
    "urllib3": {"vulnerable_below": "2.0.6", "cve": "CVE-2023-43804", "severity": "MEDIUM"},
    "numpy": {"vulnerable_below": "1.22.0", "cve": "CVE-2021-41496", "severity": "LOW"},
    "pillow": {"vulnerable_below": "10.0.1", "cve": "CVE-2023-44271", "severity": "HIGH"},
}

def parse_version(v):
    try:
        return tuple(int(x) for x in v.strip().split('.'))
    except:
        return (0, 0, 0)

def scan_dependencies(filepath):
    errors = 0
    req_path = os.path.join(os.path.dirname(filepath), "requirements.txt")
    if not os.path.exists(req_path):
        req_path = os.path.join(os.path.dirname(os.path.dirname(filepath)), "requirements.txt")
    if not os.path.exists(req_path):
        return 0
        
    print(f"\n{Fore.CYAN}[DEPS] Scanning dependencies in {req_path}...\n")
    
    with open(req_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = re.split(r'[=<>!~]+', line)
            pkg_name = parts[0].strip().lower()
            pkg_version = parts[1].strip() if len(parts) > 1 else None
            
            if pkg_name in KNOWN_VULNERABLE_PACKAGES and pkg_version:
                vuln_info = KNOWN_VULNERABLE_PACKAGES[pkg_name]
                if parse_version(pkg_version) < parse_version(vuln_info["vulnerable_below"]):
                    print(f"{Fore.RED}[X] {req_path}: {pkg_name}=={pkg_version}")
                    print(f"   {Fore.YELLOW}Issue: Known vulnerability {vuln_info['cve']} (Severity: {vuln_info['severity']})")
                    print(f"   {Fore.GREEN}Fix: Upgrade to {pkg_name}>={vuln_info['vulnerable_below']}\n")
                    errors += 1
                    
    if errors == 0:
        print(f"{Fore.GREEN}[PASS] All dependencies are up to date!\n")
    return errors

# ==========================================
# MAIN SCANNER
# ==========================================
def scan_file(filepath):
    errors_found = 0
    findings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Could not read {filepath}: {e}")
        return 1, []

    print(f"{Fore.CYAN}[SCAN] Scanning {filepath} for vulnerabilities...\n")

    for i, line in enumerate(lines):
        line_num = i + 1
        stripped = line.strip()
        
        # Skip comments
        if stripped.startswith('#'):
            continue
        
        # Check 1: Hardcoded Secrets
        for pattern, desc in SECRET_PATTERNS:
            if pattern.search(line):
                msg = f"{filepath}:{line_num} | {desc}"
                fix = "Move it to an environment variable (e.g., os.getenv('SECRET_KEY'))."
                print(f"{Fore.RED}[X] {msg}")
                print(f"   {Fore.YELLOW}Issue: {desc}")
                print(f"   {Fore.GREEN}Fix: {fix}\n")
                findings.append({"file": filepath, "line": line_num, "issue": desc, "fix": fix, "severity": "CRITICAL"})
                errors_found += 1
                break

        # Check 2: Price Tampering
        for pattern in PRICE_TAMPER_PATTERNS:
            if pattern.search(line):
                msg = "Unsafe input: Reading 'price' directly from client payload."
                fix = "Look up the price on the server-side catalog using the product_id."
                print(f"{Fore.RED}[X] {filepath}:{line_num}")
                print(f"   {Fore.YELLOW}Issue: {msg}")
                print(f"   {Fore.GREEN}Fix: {fix}\n")
                findings.append({"file": filepath, "line": line_num, "issue": msg, "fix": fix, "severity": "HIGH"})
                errors_found += 1
                break

        # Check 3: Missing Auth Decorators
        if "@app.route" in line:
            if '/api/products' not in line:
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if not next_line.startswith('@require_auth') and not next_line.startswith('@login_required'):
                        msg = "Missing authorization decorator on route."
                        fix = "Add @require_auth or @login_required above the function definition."
                        print(f"{Fore.RED}[X] {filepath}:{line_num}")
                        print(f"   {Fore.YELLOW}Issue: {msg}")
                        print(f"   {Fore.GREEN}Fix: {fix}\n")
                        findings.append({"file": filepath, "line": line_num, "issue": msg, "fix": fix, "severity": "HIGH"})
                        errors_found += 1

        # Check 4: SQL Injection
        for pattern, desc in SQL_INJECTION_PATTERNS:
            if pattern.search(line):
                fix = "Use parameterized queries (e.g., cursor.execute('SELECT * FROM users WHERE id=?', (user_id,)))."
                print(f"{Fore.RED}[X] {filepath}:{line_num}")
                print(f"   {Fore.YELLOW}Issue: {desc}")
                print(f"   {Fore.GREEN}Fix: {fix}\n")
                findings.append({"file": filepath, "line": line_num, "issue": desc, "fix": fix, "severity": "CRITICAL"})
                errors_found += 1
                break

        # Check 5: XSS
        for pattern, desc in XSS_PATTERNS:
            if pattern.search(line):
                fix = "Sanitize all user input before rendering. Use escape() or a templating engine with auto-escaping."
                print(f"{Fore.RED}[X] {filepath}:{line_num}")
                print(f"   {Fore.YELLOW}Issue: {desc}")
                print(f"   {Fore.GREEN}Fix: {fix}\n")
                findings.append({"file": filepath, "line": line_num, "issue": desc, "fix": fix, "severity": "HIGH"})
                errors_found += 1
                break

        # Check 6: PII in source code
        for pattern, desc in PII_PATTERNS:
            if pattern.search(line):
                fix = "Remove PII from source code. Store in a secure database or environment variable."
                print(f"{Fore.RED}[X] {filepath}:{line_num}")
                print(f"   {Fore.YELLOW}Issue: {desc}")
                print(f"   {Fore.GREEN}Fix: {fix}\n")
                findings.append({"file": filepath, "line": line_num, "issue": desc, "fix": fix, "severity": "HIGH"})
                errors_found += 1
                break

        # Check 7: Entropy check for possible secrets
        entropy_matches = ENTROPY_REGEX.findall(line)
        for match in entropy_matches:
            inner = match[1:-1]
            if shannon_entropy(inner) > 4.5 and len(inner) > 20:
                # Skip if already caught by other patterns
                already_caught = any(p.search(line) for p, _ in SECRET_PATTERNS)
                if not already_caught:
                    desc = "High-entropy string detected (possible secret/token)."
                    fix = "Verify this is not a secret. If it is, move it to an environment variable."
                    print(f"{Fore.YELLOW}[?] {filepath}:{line_num}")
                    print(f"   {Fore.YELLOW}Warning: {desc}")
                    print(f"   {Fore.GREEN}Fix: {fix}\n")
                    findings.append({"file": filepath, "line": line_num, "issue": desc, "fix": fix, "severity": "MEDIUM"})
                    break

    if errors_found == 0:
        print(f"{Fore.GREEN}[PASS] {filepath} passed all security checks!")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}[FAIL] Scanner found {errors_found} security flaw(s). Commit blocked!")
        
    return errors_found, findings

# ==========================================
# HTML REPORT GENERATOR
# ==========================================
def generate_html_report(all_findings, output_path):
    severity_colors = {"CRITICAL": "#dc3545", "HIGH": "#fd7e14", "MEDIUM": "#ffc107", "LOW": "#28a745"}
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>TrustIQ Security Report</title>
<style>
    body { font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #eee; }
    h1 { color: #00d4ff; border-bottom: 2px solid #00d4ff; padding-bottom: 10px; }
    h2 { color: #ff6b6b; }
    .summary { background: #16213e; padding: 20px; border-radius: 10px; margin-bottom: 30px; }
    .summary span { font-size: 2em; font-weight: bold; color: #ff6b6b; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #0f3460; color: #00d4ff; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #333; }
    tr:hover { background: #16213e; }
    .severity { padding: 4px 10px; border-radius: 4px; color: white; font-weight: bold; font-size: 0.85em; }
    .timestamp { color: #888; font-size: 0.9em; }
</style>
</head>
<body>
<h1>TrustIQ Code Inspector - Security Report</h1>
"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html += f'<p class="timestamp">Generated: {timestamp}</p>'
    
    total = len(all_findings)
    critical = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
    high = sum(1 for f in all_findings if f["severity"] == "HIGH")
    medium = sum(1 for f in all_findings if f["severity"] == "MEDIUM")
    
    html += f"""
<div class="summary">
    <p>Total Issues Found: <span>{total}</span></p>
    <p>Critical: <span style="color:#dc3545">{critical}</span> | 
       High: <span style="color:#fd7e14">{high}</span> | 
       Medium: <span style="color:#ffc107">{medium}</span></p>
</div>
"""
    
    if all_findings:
        html += """
<table>
<tr><th>File</th><th>Line</th><th>Severity</th><th>Issue</th><th>Suggested Fix</th></tr>
"""
        for f in all_findings:
            color = severity_colors.get(f["severity"], "#888")
            html += f"""<tr>
    <td>{f['file']}</td>
    <td>{f['line']}</td>
    <td><span class="severity" style="background:{color}">{f['severity']}</span></td>
    <td>{f['issue']}</td>
    <td>{f['fix']}</td>
</tr>"""
        html += "</table>"
    else:
        html += '<h2 style="color:#28a745">All files passed security checks!</h2>'
    
    html += "</body></html>"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n{Fore.MAGENTA}[REPORT] HTML report saved to: {output_path}")

# ==========================================
# MAIN
# ==========================================
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="TrustIQ Code Inspector (Pre-Commit Scanner)")
    parser.add_argument('files', nargs='+', help="Python files to scan")
    parser.add_argument('--report', type=str, default=None, help="Generate HTML report at this path")
    parser.add_argument('--deps', action='store_true', help="Also scan dependencies (requirements.txt)")
    args = parser.parse_args()

    total_errors = 0
    all_findings = []
    
    for file in args.files:
        if os.path.exists(file):
            errors, findings = scan_file(file)
            total_errors += errors
            all_findings.extend(findings)
            
            if args.deps:
                total_errors += scan_dependencies(file)
        else:
            print(f"{Fore.RED}[ERROR] File not found: {file}")
    
    if args.report:
        generate_html_report(all_findings, args.report)
    
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN} SCAN COMPLETE: {total_errors} issue(s) found across {len(args.files)} file(s)")
    print(f"{Fore.CYAN}{'='*50}")
        
    if total_errors > 0:
        sys.exit(1)
    sys.exit(0)
