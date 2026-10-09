# TrustIQ

## A Three-Layer Security System for Detecting and Preventing Web Application Vulnerabilities

> **Detect early. Defend at runtime. Learn before you commit.**

---

## 📌 Overview

**TrustIQ** is a multi-layer web application security system designed to identify, explain, and prevent common security vulnerabilities throughout the software development lifecycle.

Modern web applications often fail because security is treated as something that happens only after an application is attacked. TrustIQ takes a different approach by introducing multiple security layers:

1. **VEIL** detects security mistakes in source code before they reach production.
2. **AEGIS** protects the live application by validating and controlling incoming requests.
3. **ORACLE** allows developers to interactively analyze code snippets and understand the security problems present in them.

Together, these modules create a security workflow that focuses on **prevention, runtime protection, and developer awareness**.

### Core Philosophy

> **VEIL finds the mistake.**
> **ORACLE explains the mistake.**
> **AEGIS stops the attack.**

---

# 🎯 Problem Statement

Web applications commonly suffer from security weaknesses that can be introduced accidentally during development.

TrustIQ focuses on four major problems:

### 1. Hardcoded Passwords and API Keys

Developers sometimes directly place sensitive information inside source code.

Example:

```python
AWS_KEY = "AKIA123456789"
PASSWORD = "admin123"
API_TOKEN = "secret_token_123"
```

If this code is committed to a repository, the credentials may become exposed.

### 2. Unauthenticated Endpoints

An application may expose sensitive functionality without properly checking whether the requester is authenticated.

Example:

```text
GET /api/user/profile
```

If the endpoint does not verify authentication, an unauthorized person may access protected resources.

### 3. IDOR / Missing Ownership Checks

An application may verify that a user is logged in but fail to verify whether the requested resource actually belongs to that user.

Example:

```text
/api/user/101/profile
```

An attacker could change:

```text
101 → 102
```

and potentially access another user's information.

### 4. Payment Tampering

Applications sometimes trust sensitive values supplied by the client.

For example, the frontend sends:

```json
{
    "product_id": 15,
    "price": 5000
}
```

An attacker could modify the request:

```json
{
    "product_id": 15,
    "price": 1
}
```

If the server trusts the client-provided price, the attacker could potentially purchase an item for an incorrect amount.

---

# 🛡️ TrustIQ Architecture

TrustIQ addresses these problems through three complementary security modules.

```text
                         TRUSTIQ
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
       ┌──────┐          ┌──────┐          ┌──────┐
       │ VEIL │          │AEGIS │          │ORACLE│
       └──────┘          └──────┘          └──────┘
          │                 │                 │
          ▼                 ▼                 ▼
   Detect Problems     Block Attacks      Explain Problems
   Before Commit       At Runtime         Before Commit
```

---

# 1️⃣ VEIL

## Local Static Code Scanner

**VEIL** is the first layer of TrustIQ.

It is a **local static code scanner** designed to identify security mistakes in source code before the code is committed or deployed.

Instead of waiting for an attacker to discover a vulnerability, VEIL checks the developer's code early in the development process.

### What VEIL Looks For

VEIL can detect patterns such as:

* Hardcoded API keys
* Hardcoded passwords
* Authentication tokens
* Database credentials
* Other sensitive values accidentally placed in source code

### Example

A developer writes:

```python
DATABASE_PASSWORD = "MySecretPassword123"
```

VEIL scans the code and identifies the suspicious credential.

It can report something similar to:

```text
[HIGH] Hardcoded password detected
File: database.py
Line: 4

Recommendation:
Use an environment variable instead of storing credentials directly in source code.
```

### Why VEIL Matters

VEIL follows the principle:

> **Find security mistakes before they become security incidents.**

It acts like a security inspector for the developer's codebase.

---

# 2️⃣ AEGIS

## Zero-Trust Ingress Gateway

**AEGIS** is the runtime security layer of TrustIQ.

While VEIL works during development, AEGIS protects the application while it is running.

AEGIS sits between incoming requests and the protected application.

```text
Client
   │
   │ Request
   ▼
┌─────────────┐
│    AEGIS    │
│ Zero-Trust  │
│   Gateway   │
└─────────────┘
   │
   │ Valid Request
   ▼
Application
```

AEGIS treats every incoming request as untrusted until it has been properly validated.

### Core Responsibilities

#### Authentication Enforcement

AEGIS verifies that protected requests come from authenticated users.

Unauthenticated requests can be rejected before reaching protected application logic.

#### Ownership Checks

AEGIS verifies that the authenticated user actually owns the resource they are attempting to access.

This helps prevent IDOR vulnerabilities.

For example:

```text
User 101 → Request resource 101
```

Allowed.

But:

```text
User 101 → Request resource 102
```

Rejected unless the user is legitimately authorized to access it.

#### Server-Side Price Validation

AEGIS does not blindly trust prices received from the client.

Instead, the server-side catalog is treated as the trusted source.

For example:

```text
Client says:
price = ₹1

Server catalog:
actual price = ₹5000
```

AEGIS can reject the manipulated request.

#### Request Validation

AEGIS validates incoming requests before allowing them to reach protected application functionality.

#### Security Logging

Blocked requests can be recorded along with the reason for rejection.

Example:

```text
BLOCKED REQUEST
Reason: Ownership check failed
User: 101
Requested Resource: 102
```

### AEGIS Philosophy

> **Never trust the request simply because it reached the server.**

---

# 3️⃣ ORACLE

## Interactive Security Code Analyzer

**ORACLE** is the third module of TrustIQ.

Unlike VEIL, which automatically scans project files, ORACLE allows a developer to manually paste a code snippet and ask the security engine to analyze it.

The developer interacts with ORACLE through a self-hosted web application.

### Basic Workflow

```text
Developer
    │
    │ Paste Code
    ▼
ORACLE Frontend
    │
    │ POST /dashboard/scan
    ▼
proxy.py
    │
    ▼
Security Analyzer
    │
    ├── secrets.py
    ├── injection.py
    └── credentials.py
    │
    ▼
JSON Findings
    │
    ▼
ORACLE Frontend
    │
    ▼
Developer sees security report
```

---

## ORACLE Example

A developer pastes:

```python
AWS_KEY = "AKIA123456789"

password = "admin123"

query = "SELECT * FROM users WHERE id = " + user_id
```

The developer clicks:

```text
ANALYZE
```

ORACLE processes the code and returns deterministic findings.

For example:

```text
3 security issues detected.

[HIGH]
Line 1:
Hardcoded AWS/API credential detected.

Recommendation:
Move the credential to a secure environment variable or secret manager.

[HIGH]
Line 3:
Potential SQL injection surface detected.

Recommendation:
Use parameterized queries instead of directly constructing SQL strings.

[HIGH]
Line 3:
User-controlled data appears to be inserted directly into a database query.
```

---

# 🔍 ORACLE Backend Architecture

The ORACLE backend is organized into separate components so that each part has a clear responsibility.

```text
ORACLE/
│
├── proxy.py
│
├── analyzer/
│   ├── __init__.py
│   ├── scanner.py
│   ├── secrets.py
│   ├── injection.py
│   └── credentials.py
│
├── frontend/
│   └── index.html
│
└── requirements.txt
```

---

## `proxy.py`

`proxy.py` acts as the backend server and communication layer.

Its main responsibilities include:

* Receiving code from the frontend
* Providing the `/dashboard/scan` endpoint
* Passing submitted code to the analyzer
* Returning the analysis results as JSON

Example endpoint:

```python
@app.route('/dashboard/scan')
```

The frontend sends the pasted code to this endpoint.

---

## `analyzer/`

The `analyzer` directory contains the actual security-analysis logic.

It is separated into multiple files so that different types of security checks can be maintained independently.

---

## `__init__.py`

This file marks the `analyzer` directory as a Python package.

It can initially remain empty.

---

## `scanner.py`

`scanner.py` acts as the coordinator for the security analysis.

Instead of putting every security rule into one large file, the scanner can call the appropriate modules.

For example:

```text
scanner.py
    │
    ├── secrets.py
    ├── injection.py
    └── credentials.py
```

The scanner combines their findings into one final result.

---

## `secrets.py`

This module focuses on detecting potentially hardcoded secrets.

Examples include:

```python
API_KEY = "abc123"
```

```python
AWS_KEY = "AKIA..."
```

```python
TOKEN = "secret-token"
```

The module can use pattern matching and regular expressions to identify suspicious assignments.

---

## `injection.py`

This module focuses on potentially dangerous input handling and injection surfaces.

For example:

```python
query = "SELECT * FROM users WHERE id = " + user_id
```

The analyzer can flag direct string construction involving user-controlled input.

---

## `credentials.py`

This module focuses on credentials such as:

* Passwords
* Database usernames
* Database passwords
* Authentication credentials

Example:

```python
DB_PASSWORD = "mypassword"
```

---

# 🌐 ORACLE Frontend

The frontend is located at:

```text
frontend/index.html
```

It provides the interface through which developers interact with ORACLE.

The frontend allows the developer to:

1. Paste code
2. Click Analyze
3. Send the code to the backend
4. Receive the security report
5. Display the results

The JavaScript function can perform the request using:

```javascript
fetch()
```

The basic flow is:

```text
Paste Code
     │
     ▼
analyzeCode()
     │
     ▼
fetch("/dashboard/scan")
     │
     ▼
Python Backend
     │
     ▼
Security Analysis
     │
     ▼
JSON Response
     │
     ▼
Chatbox / Results Panel
```

---

# 🔄 JSON Communication

ORACLE uses **JSON** to communicate between the frontend and backend.

JSON is a standard format for representing structured data.

For example, the frontend can send:

```json
{
    "code": "password = \"admin123\""
}
```

The backend analyzes the code and can return:

```json
{
    "count": 1,
    "findings": [
        {
            "line": 1,
            "type": "Hardcoded Password",
            "severity": "HIGH",
            "message": "A hardcoded password was detected.",
            "recommendation": "Use an environment variable."
        }
    ]
}
```

The frontend then reads this JSON and displays the result to the developer.

---

# 🎯 Deterministic Analysis

A major design principle of ORACLE is **deterministic analysis**.

This means:

> **The same input should produce the same result.**

For example:

```text
Input:
password = "admin123"
```

should consistently produce the same security finding.

ORACLE does not need to depend on an unpredictable AI model to determine whether a known pattern is suspicious.

Instead, it can use:

* Regular expressions
* Pattern matching
* Static analysis rules
* Security heuristics
* Deterministic scoring

This makes the security verdict reproducible and easier to demonstrate during the hackathon.

---

# 🧩 Difference Between VEIL and ORACLE

Although VEIL and ORACLE both analyze source code, they serve different purposes.

| Feature               | VEIL                       | ORACLE                           |
| --------------------- | -------------------------- | -------------------------------- |
| Purpose               | Automated project scanning | Interactive code analysis        |
| Input                 | Project/source files       | Pasted code snippet              |
| Usage                 | Local/pre-commit           | Self-hosted web application      |
| Developer interaction | Mostly automatic           | Manual                           |
| Output                | Security findings          | Interactive security explanation |
| Main purpose          | Catch mistakes early       | Explain and investigate mistakes |

### Simple Explanation

**VEIL:**

> "I will scan your project and tell you if something looks dangerous."

**ORACLE:**

> "Give me this piece of code and I will explain what security problems it contains."

---

# 🔐 TrustIQ Security Workflow

The three modules work at different stages of the development and application lifecycle.

```text
                 DEVELOPMENT
                      │
                      ▼
             ┌────────────────┐
             │      VEIL      │
             │ Static Scanner │
             └────────────────┘
                      │
               Security Check
                      │
                      ▼
             ┌────────────────┐
             │     ORACLE     │
             │ Code Analyzer  │
             └────────────────┘
                      │
                Understand &
                Fix Problems
                      │
                      ▼
                 APPLICATION
                      │
                      ▼
             ┌────────────────┐
             │     AEGIS      │
             │ Runtime Guard  │
             └────────────────┘
                      │
                      ▼
               Protected App
```

---

# ⭐ Key Features

## 1. Early Detection

VEIL helps developers detect security mistakes before they reach production.

## 2. Interactive Security Analysis

ORACLE allows developers to directly investigate suspicious code.

## 3. Runtime Protection

AEGIS validates requests while the application is running.

## 4. Hardcoded Secret Detection

TrustIQ identifies potentially exposed:

* API keys
* Passwords
* Tokens
* Database credentials

## 5. Injection Detection

TrustIQ can identify suspicious patterns that may create injection vulnerabilities.

## 6. Authentication Protection

AEGIS helps ensure that protected endpoints are not accessible to unauthenticated users.

## 7. Ownership Validation

AEGIS prevents users from accessing resources that they do not own.

## 8. Payment Integrity

AEGIS validates sensitive payment values using trusted server-side information.

## 9. Security Logging

Blocked requests can be recorded for auditing and debugging.

## 10. Deterministic Results

ORACLE produces reproducible results from the same input.

---

# 🧪 Example Demonstration Scenarios

TrustIQ can demonstrate several common attack/security scenarios.

---

## Scenario 1 — Hardcoded Secret

### Vulnerable Code

```python
API_KEY = "my-secret-key"
```

### Detection

VEIL or ORACLE identifies the hardcoded secret.

### Recommended Fix

```python
import os

API_KEY = os.getenv("API_KEY")
```

---

## Scenario 2 — Unsafe SQL Construction

### Vulnerable Code

```python
query = "SELECT * FROM users WHERE id = " + user_id
```

### Detection

ORACLE identifies a potential SQL injection surface.

### Recommended Fix

Use parameterized database queries rather than directly inserting user-controlled input into SQL.

---

## Scenario 3 — IDOR

### Vulnerable Request

```text
GET /api/user/102
```

A user authenticated as User 101 attempts to access User 102's resource.

### AEGIS

AEGIS performs an ownership check.

```text
Authenticated User: 101
Requested Resource: 102

Ownership Check: FAILED

Request: BLOCKED
```

---

## Scenario 4 — Payment Tampering

### Original Price

```text
₹5000
```

### Attacker Request

```json
{
    "product_id": 15,
    "price": 1
}
```

### AEGIS

AEGIS compares the submitted value with the trusted server-side price.

```text
Client Price: ₹1
Server Price: ₹5000

Price Validation: FAILED

Request: BLOCKED
```

---

# 🏗️ Suggested Repository Structure

The complete TrustIQ repository can be organized approximately as follows:

```text
TrustIQ/
│
├── VEIL/
│   ├── scanner/
│   ├── rules/
│   ├── tests/
│   └── README.md
│
├── AEGIS/
│   ├── gateway/
│   ├── middleware/
│   ├── validation/
│   ├── logging/
│   └── README.md
│
├── ORACLE/
│   ├── proxy.py
│   │
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── scanner.py
│   │   ├── secrets.py
│   │   ├── injection.py
│   │   └── credentials.py
│   │
│   ├── frontend/
│   │   └── index.html
│   │
│   ├── requirements.txt
│   └── README.md
│
├── README.md
└── LICENSE
```

The exact internal structure can be adjusted depending on the implementation of each module.

---

# ⚙️ Technology Stack

## VEIL

* Python
* Static analysis
* Regular expressions / pattern matching
* Local CLI or pre-commit integration

## AEGIS

* Python
* HTTP request handling
* Authentication/authorization validation
* Server-side validation
* Request logging

## ORACLE

* Python
* Flask-style backend
* HTML
* CSS
* JavaScript
* JSON
* Regular expressions
* Static security analysis

---

# 📦 ORACLE Requirements

The ORACLE backend dependencies can be maintained inside:

```text
requirements.txt
```

Dependencies can be installed using:

```bash
pip install -r requirements.txt
```

The exact dependency list depends on the final backend implementation.

---

# 🚀 Running ORACLE

Once the ORACLE backend is configured, the application can be started locally.

Example:

```bash
python proxy.py
```

The local server can then expose the ORACLE interface and API.

The frontend communicates with:

```text
POST /dashboard/scan
```

to submit code for analysis.

---

# 🔄 ORACLE Request Flow

A complete request looks like this:

```text
1. Developer opens ORACLE

        ↓

2. Developer pastes code

        ↓

3. Developer clicks ANALYZE

        ↓

4. JavaScript collects the code

        ↓

5. Frontend sends JSON request

        ↓

6. proxy.py receives the request

        ↓

7. scanner.py starts analysis

        ↓

8. Security modules inspect the code

        ├── secrets.py
        ├── injection.py
        └── credentials.py

        ↓

9. Findings are combined

        ↓

10. Backend returns JSON

        ↓

11. Frontend displays the results
```

---

# 📊 Example ORACLE Response

A successful analysis could return:

```json
{
    "count": 2,
    "findings": [
        {
            "line": 2,
            "type": "Hardcoded Credential",
            "severity": "HIGH",
            "message": "A possible hardcoded password was detected.",
            "recommendation": "Use an environment variable or secure secret manager."
        },
        {
            "line": 5,
            "type": "Potential Injection",
            "severity": "HIGH",
            "message": "User-controlled input appears to be directly inserted into a query.",
            "recommendation": "Use parameterized queries."
        }
    ]
}
```

This structured format allows the frontend to present the findings clearly.

---

# 🧠 Security Philosophy

TrustIQ follows a simple principle:

> **Do not wait for the attacker to find the vulnerability.**

Instead:

```text
Developer makes mistake
        │
        ▼
      VEIL
        │
        ▼
Mistake detected early
        │
        ▼
Developer investigates
        │
        ▼
      ORACLE
        │
        ▼
Problem understood and fixed
        │
        ▼
Application deployed
        │
        ▼
      AEGIS
        │
        ▼
Malicious request blocked
```

This creates multiple opportunities to stop a security problem.

---

# 🎯 Project Objective

The primary objective of TrustIQ is to build a practical security system that combines:

* **Static security analysis**
* **Interactive developer assistance**
* **Runtime request protection**
* **Authentication and authorization checks**
* **Ownership validation**
* **Sensitive-value validation**
* **Security logging**
* **Deterministic security analysis**

The goal is not simply to detect vulnerabilities but to create a layered security workflow where vulnerabilities can be **detected, understood, and prevented**.

---

# 💡 Why Three Modules?

A single security tool cannot cover every stage of an application's lifecycle.

### VEIL

Protects the **development stage**.

> "Is there something dangerous in the code?"

### ORACLE

Protects the **developer's understanding stage**.

> "What exactly is wrong with this code and how should I fix it?"

### AEGIS

Protects the **runtime stage**.

> "Is this incoming request actually allowed?"

Together:

```text
             DEVELOPMENT
                  │
                VEIL
                  │
                  ▼
            ORACLE
                  │
                  ▼
             DEPLOYMENT
                  │
                  ▼
               AEGIS
                  │
                  ▼
             PROTECTED
            APPLICATION
```

---

# 🏆 Expected Outcome

At the end of the project, TrustIQ should demonstrate that a web application can be protected through multiple security layers.

A successful demonstration should show:

### Before Deployment

VEIL identifies insecure code.

### During Development

ORACLE allows developers to paste suspicious code and receive a clear security explanation.

### During Runtime

AEGIS blocks unauthorized or manipulated requests.

This demonstrates a complete security lifecycle rather than a single isolated security feature.

---

# 📌 Core TrustIQ Message

> ### VEIL finds the mistake.
>
> ### ORACLE explains the mistake.
>
> ### AEGIS stops the attack.

TrustIQ therefore combines **detection, understanding, and prevention** into one security architecture.

---

# 🔮 Future Improvements

Potential future improvements include:

* Additional secret-detection rules
* More injection detection techniques
* Support for additional programming languages
* Improved security severity scoring
* More detailed security reports
* Integration with Git hooks
* CI/CD pipeline integration
* Expanded authentication checks
* More advanced ownership policies
* Security dashboards
* Audit-log visualization
* Additional vulnerability categories

---

# ⚠️ Disclaimer

TrustIQ is a security research and educational project developed for authorized testing and demonstration purposes.

It should only be used to analyze code and applications that you own or have explicit permission to test.

The detection mechanisms are rule-based and may produce false positives or fail to identify sophisticated vulnerabilities. TrustIQ should therefore be treated as a security-assistance tool rather than a replacement for a professional security audit.

---

# 👥 Project Modules

| Module   | Name       | Primary Role                       |
| -------- | ---------- | ---------------------------------- |
| Module 1 | **VEIL**   | Local Static Code Scanner          |
| Module 2 | **AEGIS**  | Zero-Trust Ingress Gateway         |
| Module 3 | **ORACLE** | Interactive Security Code Analyzer |

---

# 🔐 TrustIQ

**Detect early. Defend at runtime. Learn before you commit.**

> **VEIL finds the mistake. ORACLE explains the mistake. AEGIS stops the attack.**
