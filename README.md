# 🛡️ TrustIQ: The Future of Developer-First Security

[![DevSecOps Hackathon](https://img.shields.io/badge/Hackathon-DevSecOps-blue.svg)](#)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

> **"Security shouldn't be an afterthought. It should be invisible, intelligent, and integrated."**

TrustIQ is a next-generation DevSecOps ecosystem designed to catch vulnerabilities before they reach the cloud and neutralize active attacks at the edge. By bridging the gap between local development and live production, TrustIQ provides a true end-to-end security pipeline.

---

## 🏗️ Architecture & Modules

TrustIQ is composed of three interconnected security modules, each targeting a specific layer of the DevSecOps lifecycle, built around our intentionally vulnerable testbed application, **Vanguard**.

### 1. 🕵️ Veil (Pre-Commit Scanner)
**Prevention over Damage Control.**
Traditional scanners like GitHub Advanced Security only catch secrets *after* they are pushed to the cloud, meaning the secret is permanently etched into your commit history and must be revoked. 
* **Air-Gapped & Local:** Veil runs entirely on the developer's local machine via Git hooks.
* **Shannon Entropy Engine:** While competitors rely strictly on Regex (missing custom internal tokens), Veil calculates the mathematical randomness of strings to flag high-entropy zero-day secrets.
* **Outcome:** The commit is physically blocked. The secret never touches the `.git` history.

### 2. 🛡️ Aegis (Zero-Trust Proxy / WAF)
**Live Attack Neutralization.**
Aegis sits between the client and the backend server, inspecting every packet in real-time. It acts as an intelligent firewall for the modern web.
* **Price Tampering Prevention:** Verifies checkout cart payloads against backend catalog truth.
* **Privilege Escalation & IDOR:** Drops injected restricted headers (e.g., `is-admin`) and validates authorization contexts.
* **SQLi & XSS Mitigation:** Sanitizes and blocks malicious payloads targeting database and DOM execution.
* **Real-Time Dashboard:** Provides instant telemetry on blocked attacks, rate limits, and banned IPs.

### 3. 🤖 Oracle (Interactive Security AI)
**Developer Enablement.**
Oracle is an interactive DevSecOps chatbox designed to help developers understand *why* their code was blocked and how to fix it, reducing friction between security teams and engineering.

### 🎯 Vanguard (The Target)
**The Proving Ground.**
Vanguard (and its backend, Nova) is our custom-built, intentionally vulnerable e-commerce application. It serves as the honeypot to demonstrate TrustIQ's capabilities. 
* Includes simulated attacks for XSS, SQL Injection, Privilege Escalation (Malicious Headers), and Price Tampering.

---

## 🚀 Quick Start (Demo Tunnels)

For the hackathon presentation, the TrustIQ ecosystem is hosted live via persistent local tunnels.

* **Main TrustIQ Dashboard:** [https://trustiq-demo.loca.lt/frontend/index.html](https://trustiq-demo.loca.lt/frontend/index.html)
* **Vanguard Vulnerable App:** [https://trustiq-demo.loca.lt/vanguard.html](https://trustiq-demo.loca.lt/vanguard.html)
* **Aegis Proxy Endpoint (API):** `https://trustiq-aegis.loca.lt` *(Handled automatically by the UI)*

*(Note: When opening the Dashboard or Vanguard for the first time, simply click the blue "Click to Continue" button to bypass the Localtunnel anti-phishing screen.)*

---

## 🛠️ How to Run Locally

If you wish to spin up the entire TrustIQ ecosystem on your local machine:

**1. Clone the repository**
```bash
git clone https://github.com/aryang-0908/TrustIQ.git
cd TrustIQ
```

**2. Start the Vulnerable Backend (Vanguard/Nova)**
```bash
cd devsecops_hackathon/practice_shop
python app_vulnerable.py
# Runs on http://127.0.0.1:8001
```

**3. Start the Aegis Proxy**
```bash
cd devsecops_hackathon/proxy
python proxy.py
# Runs on http://127.0.0.1:8000
```

**4. Start the Frontend Server**
```bash
cd devsecops_hackathon
python -m http.server 3000
# Accessible at http://127.0.0.1:3000/frontend/index.html
```

---

## ⚔️ Live Demo Scenarios

During the pitch, we demonstrate the following attack vectors on the Vanguard application:

1. **The Price Tampering Hack:** Using the Vanguard UI to change the price of a $50,000 server to $1. **Result:** Aegis validates the catalog and blocks the transaction.
2. **The Privilege Escalation:** Injecting the `is-admin: true` HTTP header to access restricted APIs. **Result:** Aegis detects the restricted header and returns a `403 FORBIDDEN`.
3. **The Pre-Commit Save:** Attempting to commit an AWS API key to the repository. **Result:** Veil's Shannon Entropy engine stops the commit execution locally.

---

## 🏆 Why TrustIQ?

TrustIQ was built for the **DevSecOps Hackathon** to prove that robust security doesn't have to slow down development. By combining mathematically advanced local scanning (Veil) with intelligent edge routing (Aegis), we give developers the tools to build fast and build safe.
