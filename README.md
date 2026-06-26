# 📈 Personal Finance Ledger Core (REST API Backend)

A high-utility, secure, and production-optimized personal finance API engine built with **Django** and **Django REST Framework (DRF)**. This system implements a high-performance **Single-Table Architecture** to track liquid assets, cash pools, and credit liability lines within a single, highly efficient database layer.

---

## 🚀 Core Architectural Highlights

*   🔐 **Multi-Tenant Security Guards**: Enforces strict user-level data isolation. Users can strictly query, modify, or view only their own financial profiles and datasets.
*   💳 **Unified Balance Engine**: Tracks standard cash wallets, digital bank accounts, and credit/loan buckets inside a single database table. It manages debts natively using inverse mathematics and custom python models.
*   🛡️ **Airtight Serializer Safeguards**: Defense-in-depth API rules that actively block impossible real-world transactions (such as transferring physical paper cash directly into a digital bank) and automatically prevent credit card over-spending.
*   🔄 **Automatic Balance Reversals**: Overridden deletion view methods intercept transaction deletions on the fly to compute reverse math and automatically heal connected wallet parameters.
*   ⚡ **High-Performance Analytics**: Employs database-level SQL aggregation and grouping filters instead of slow Python memory loops, maintaining a rapid O(1) memory footprint even over a 10-year data timeline.

---

## 🛠️ Technology Framework

| Layer | Component | Description |
| :--- | :--- | :--- |
| **Backend Core** | Django & DRF | REST API development, security hooks, and router pipelines |
| **Database** | SQLite / PostgreSQL | Structured relational ledger storage layer |
| **Authentication**| Simple JWT | Secure, stateless token-based identity verification |
| **Environment** | python-dotenv | Decoupled production-ready secret variable configuration |

---

## ⚡ Setup & Installation Guidelines

1. Clone the repository and initialize a localized python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows use: venv\Scripts\activate
   ```

2. Pull all required software dependencies inside your active environment:
   ```bash
   pip install -r requirements.txt
   ```

3. Construct a secure `.env` file in the project's root folder directory:
   ```ini
   SECRET_KEY="your_django_secret_cryptography_key"
   DEBUG=True
   CORS_ALLOWED_ORIGINS_STR=http://localhost:5173
   ```

4. Compile and run your database schema migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Launch your localized development server infrastructure network:
   ```bash
   python manage.py runserver
   ```
