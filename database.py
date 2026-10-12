import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "banking.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                account_number TEXT NOT NULL,
                account_type TEXT NOT NULL,
                balance REAL NOT NULL,
                monthly_salary REAL NOT NULL,
                existing_emi REAL NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS loan_applications (
                application_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                loan_amount REAL NOT NULL,
                tenure_months INTEGER NOT NULL,
                annual_interest_rate REAL NOT NULL,
                monthly_emi REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            )
        """)

        # Fictional training data only.
        conn.execute("""
            INSERT OR IGNORE INTO customers
            (customer_id, full_name, account_number, account_type,
             balance, monthly_salary, existing_emi)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "CUST1001",
            "Rahul Sharma",
            "XXXXXX1234",
            "Savings",
            125000.00,
            60000.00,
            5000.00
        ))


if __name__ == "__main__":
    init_db()
    print(f"Database initialized: {DB_PATH}")
    print("Demo customer: CUST1001")
