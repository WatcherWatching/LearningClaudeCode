import sqlite3
from datetime import date, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

# Database file lives at the project root, alongside app.py.
DB_PATH = Path(__file__).resolve().parent.parent / "spendly.db"


def get_db():
    """Open a SQLite connection with row_factory and foreign-key enforcement enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables. Safe to call multiple times."""
    conn = get_db()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def seed_db():
    """Insert a demo user and 8 sample expenses. Skips if users table is non-empty."""
    conn = get_db()
    try:
        existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if existing > 0:
            return

        # Demo user
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", generate_password_hash("demo123")),
        )
        user_id = conn.execute(
            "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
        ).fetchone()["id"]

        # 8 sample expenses, covering all 7 categories within the current month.
        today = date.today()
        first_of_month = today.replace(day=1)
        samples = [
            (1, 250.0,  "Food",          "Groceries"),
            (2, 60.0,   "Transport",     "Bus pass"),
            (3, 1200.0, "Bills",         "Electricity bill"),
            (4, 450.0,  "Health",        "Pharmacy"),
            (5, 350.0,  "Entertainment", "Movie tickets"),
            (6, 899.0,  "Shopping",      "New shoes"),
            (7, 150.0,  "Other",         "Misc supplies"),
            (8, 180.0,  "Food",          "Dinner out"),
        ]

        for days_into_month, amount, category, description in samples:
            # Stay within the current month: clamp the day to the month's last day.
            last_day = (first_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
            last_day = last_day - timedelta(days=1)
            day = min(days_into_month, last_day.day)
            expense_date = first_of_month.replace(day=day).isoformat()
            conn.execute(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                (user_id, amount, category, expense_date, description),
            )

        conn.commit()
    finally:
        conn.close()
