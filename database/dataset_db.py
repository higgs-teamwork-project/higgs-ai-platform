from pathlib import Path
from typing import Iterable, Optional
import sqlite3


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "dataset.db"


def get_connection() -> sqlite3.Connection:
    """
    Connection to the dataset database (donors, NGOs, and matches).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_schema() -> None:
    """
    Create tables for donors, NGOs, and matches if they do not exist.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS donors (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                sectors         TEXT,
                regions         TEXT,
                description     TEXT,
                keywords        TEXT,
                embedding       BLOB,
                created_at      TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ngos (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                name            TEXT NOT NULL,
                sectors         TEXT,
                regions         TEXT,
                description     TEXT,
                keywords        TEXT,
                embedding       BLOB,
                created_at      TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS donor_ngo_matches (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_id        INTEGER NOT NULL,
                ngo_id          INTEGER NOT NULL,
                similarity      REAL NOT NULL,
                notes           TEXT,
                created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (donor_id, ngo_id),
                FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE,
                FOREIGN KEY (ngo_id) REFERENCES ngos(id) ON DELETE CASCADE
            )
            """
        )

        conn.commit()
    finally:
        conn.close()


def insert_donor(
    name: str,
    sectors: Optional[Iterable[str]] = None,
    regions: Optional[Iterable[str]] = None,
    description: Optional[str] = None,
    keywords: Optional[Iterable[str]] = None,
    embedding: Optional[bytes] = None,
) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO donors (name, sectors, regions, description, keywords, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                _join(sectors),
                _join(regions),
                description,
                _join(keywords),
                embedding,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def insert_ngo(
    name: str,
    sectors: Optional[Iterable[str]] = None,
    regions: Optional[Iterable[str]] = None,
    description: Optional[str] = None,
    keywords: Optional[Iterable[str]] = None,
    embedding: Optional[bytes] = None,
) -> int:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO ngos (name, sectors, regions, description, keywords, embedding)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                _join(sectors),
                _join(regions),
                description,
                _join(keywords),
                embedding,
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_donors() -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM donors ORDER BY id")
        return cur.fetchall()
    finally:
        conn.close()


def list_ngos() -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ngos ORDER BY id")
        return cur.fetchall()
    finally:
        conn.close()


def _join(values: Optional[Iterable[str]]) -> Optional[str]:
    if values is None:
        return None
    cleaned = [v.strip() for v in values if v and v.strip()]
    return ", ".join(cleaned) if cleaned else None

