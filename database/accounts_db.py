from pathlib import Path
import os
import sqlite3
import hashlib


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "accounts.db"


def get_connection() -> sqlite3.Connection:
    """
    Connection to the accounts database (usernames + password hashes).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_schema() -> None:
    """
    Create the accounts table if it does not exist.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT NOT NULL UNIQUE,
                password_hash   TEXT NOT NULL,
                salt            TEXT NOT NULL,
                role            TEXT,
                created_at      TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def create_account(username: str, password: str, role: str | None = None) -> int:
    """
    Create a new account with a salted SHA-256 hash of the password.
    """
    salt = os.urandom(16).hex()
    password_hash = _hash_password(password, salt)

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO accounts (username, password_hash, salt, role)
            VALUES (?, ?, ?, ?)
            """,
            (username, password_hash, salt, role),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def verify_credentials(username: str, password: str) -> bool:
    """
    Check whether the provided username/password combination is valid.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT password_hash, salt FROM accounts WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        if row is None:
            return False
        expected_hash = row["password_hash"]
        salt = row["salt"]
        return _hash_password(password, salt) == expected_hash
    finally:
        conn.close()


def _hash_password(password: str, salt: str) -> str:
    data = (salt + password).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

