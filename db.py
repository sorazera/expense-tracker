import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "expenses.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    opening_balance INTEGER NOT NULL DEFAULT 0   -- in centavos
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    kind TEXT NOT NULL CHECK (kind IN ('expense', 'income'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,                          -- YYYY-MM-DD
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    amount INTEGER NOT NULL CHECK (amount > 0),  -- in centavos
    note TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""

DEFAULT_ACCOUNTS = ["GCash", "GoTyme", "Cash"]
DEFAULT_CATEGORIES = [
    ("Food", "expense"), ("Transport", "expense"), ("Bills", "expense"),
    ("School", "expense"), ("Shopping", "expense"), ("Other", "expense"),
    ("Allowance", "income"), ("Salary", "income"), ("Other income", "income"),
]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with connect() as conn:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT OR IGNORE INTO accounts (name) VALUES (?)",
            [(name,) for name in DEFAULT_ACCOUNTS],
        )
        conn.executemany(
            "INSERT OR IGNORE INTO categories (name, kind) VALUES (?, ?)",
            DEFAULT_CATEGORIES,
        )


def to_centavos(pesos: float) -> int:
    return round(pesos * 100)


def to_pesos(centavos: int) -> float:
    return centavos / 100


def get_accounts():
    with connect() as conn:
        return conn.execute("SELECT id, name FROM accounts ORDER BY name").fetchall()


def get_categories(kind):
    with connect() as conn:
        return conn.execute(
            "SELECT id, name FROM categories WHERE kind = ? ORDER BY name",
            (kind,),
        ).fetchall()


def add_transaction(date, account_id, category_id, amount_centavos, note):
    with connect() as conn:
        conn.execute(
            "INSERT INTO transactions (date, account_id, category_id, amount, note)"
            " VALUES (?, ?, ?, ?, ?)",
            (date, account_id, category_id, amount_centavos, note or None),
        )


def recent_transactions(limit=5):
    with connect() as conn:
        return conn.execute(
            """
            SELECT t.date, a.name AS account, c.name AS category, c.kind,
                   t.amount, t.note
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            JOIN categories c ON c.id = t.category_id
            ORDER BY t.date DESC, t.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


if __name__ == "__main__":
    init_db()
    with connect() as conn:
        accounts = [r["name"] for r in conn.execute("SELECT name FROM accounts")]
        categories = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    print(f"Database ready at {DB_PATH}")
    print(f"Accounts: {', '.join(accounts)}")
    print(f"Categories: {categories}")