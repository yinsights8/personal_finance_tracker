import sqlite3
from datetime import datetime
from shared.config import DATABASE_NAME

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            address TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN address TEXT DEFAULT ''")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT DEFAULT ''")
    except Exception:
        pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    from features.auth.service import hash_password
    cursor.execute(
        "INSERT INTO users (name, email, password_hash, address, phone) VALUES (?, ?, ?, ?, ?)",
        ("Demo User", "demo@spendly.com", hash_password("demo123"), "123 Main St, City", "+1-555-0123")
    )
    user_id = cursor.lastrowid

    today = datetime.now()
    expenses = [
        (user_id, 45.50, "Food", f"{today.year}-{today.month:02d}-02", "Lunch with colleagues"),
        (user_id, 25.00, "Transport", f"{today.year}-{today.month:02d}-03", "Monthly bus pass"),
        (user_id, 150.00, "Bills", f"{today.year}-{today.month:02d}-05", "Electricity bill"),
        (user_id, 80.00, "Health", f"{today.year}-{today.month:02d}-07", "Pharmacy"),
        (user_id, 35.00, "Entertainment", f"{today.year}-{today.month:02d}-10", "Movie tickets"),
        (user_id, 120.00, "Shopping", f"{today.year}-{today.month:02d}-12", "New shoes"),
        (user_id, 15.00, "Other", f"{today.year}-{today.month:02d}-14", "Miscellaneous"),
        (user_id, 60.00, "Food", f"{today.year}-{today.month:02d}-15", "Grocery shopping"),
    ]

    for expense in expenses:
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expense
        )

    conn.commit()
    conn.close()
