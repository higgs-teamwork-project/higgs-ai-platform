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
                legal_form      TEXT,
                strategy        TEXT,
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
                legal_form      TEXT,
                strategy        TEXT,
                focus           TEXT,
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
    legal_form: Optional[str] = None,
    strategy: Optional[str] = None,
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
            INSERT INTO donors (name, legal_form, strategy, sectors, regions, description, keywords, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                legal_form,
                strategy,
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
    legal_form: Optional[str] = None,
    strategy: Optional[str] = None,
    focus: Optional[str] = None,
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
            INSERT INTO ngos (name, legal_form, strategy, focus, sectors, regions, description, keywords, embedding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                legal_form,
                strategy,
                focus,
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


def get_donor(donor_id: int) -> Optional[sqlite3.Row]:
    """
    Return a single donor row by ID, or None if it does not exist.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM donors WHERE id = ?", (donor_id,))
        return cur.fetchone()
    finally:
        conn.close()


def get_ngo(ngo_id: int) -> Optional[sqlite3.Row]:
    """
    Return a single NGO row by ID, or None if it does not exist.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM ngos WHERE id = ?", (ngo_id,))
        return cur.fetchone()
    finally:
        conn.close()


def delete_ngo(ngo_id: int) -> bool:
    """
    Delete one NGO by ID. Also removes donor_ngo_matches for this NGO.
    Returns True if a row was deleted.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM donor_ngo_matches WHERE ngo_id = ?", (ngo_id,))
        cur.execute("DELETE FROM ngos WHERE id = ?", (ngo_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def delete_ngos(ngo_ids: Iterable[int]) -> int:
    """
    Delete multiple NGOs by ID. Also removes donor_ngo_matches for them.
    Returns the number of NGOs deleted.
    """
    ids = list(ngo_ids)
    if not ids:
        return 0
    conn = get_connection()
    try:
        cur = conn.cursor()
        placeholders = ",".join("?" * len(ids))
        cur.execute(f"DELETE FROM donor_ngo_matches WHERE ngo_id IN ({placeholders})", ids)
        cur.execute(f"DELETE FROM ngos WHERE id IN ({placeholders})", ids)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()

# Added new delete_donor
def delete_donors(donor_ids: Iterable[int]) -> int:
    """Delete multiple donors by ID. Also removes donor_ngo_matches for them."""
    ids = list(donor_ids)
    if not ids:
        return 0
    conn = get_connection()
    try:
        cur = conn.cursor()
        placeholders = ",".join("?" * len(ids))
        cur.execute(f"DELETE FROM donor_ngo_matches WHERE donor_id IN ({placeholders})", ids)
        cur.execute(f"DELETE FROM donors WHERE id IN ({placeholders})", ids)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def update_donor_embedding(donor_id: int, embedding: bytes) -> None:
    """
    Update the embedding column for a donor.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE donors SET embedding = ? WHERE id = ?",
            (embedding, donor_id),
        )
        conn.commit()
    finally:
        conn.close()


def update_ngo_embedding(ngo_id: int, embedding: bytes) -> None:
    """
    Update the embedding column for an NGO.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE ngos SET embedding = ? WHERE id = ?",
            (embedding, ngo_id),
        )
        conn.commit()
    finally:
        conn.close()


def save_match(
    donor_id: int,
    ngo_id: int,
    similarity: float,
    notes: Optional[str] = None,
) -> int:
    """
    Insert or update a donor/NGO match with a similarity score.
    Returns the ID of the match row.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO donor_ngo_matches (donor_id, ngo_id, similarity, notes)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(donor_id, ngo_id) DO UPDATE SET
                similarity = excluded.similarity,
                notes = COALESCE(excluded.notes, donor_ngo_matches.notes)
            """,
            (donor_id, ngo_id, similarity, notes),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()

def list_matches_for_donor(donor_id: int) -> list[sqlite3.Row]:
    """
    Retrieve all matches for specific donor. 
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT a.donor_id, a.ngo_id, b.name, b.strategy, b.focus, b.sectors, a.similarity
            FROM donor_ngo_matches a
            JOIN ngos b ON a.ngo_id = b.id
            WHERE donor_id = ?
            ORDER BY similarity DESC
            """
        , (donor_id,))
        return cur.fetchall()
    finally:
        conn.close()

def list_all_matches() -> list[sqlite3.Row]:
    """
    Retrieve all saved matches. 
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT donor_id, ngo_id
            FROM donor_ngo_matches
            """
        )
        return cur.fetchall()
    finally:
        conn.close()

def _join(values: Optional[Iterable[str]]) -> Optional[str]:
    if values is None:
        return None
    cleaned = [v.strip() for v in values if v and v.strip()]
    return ", ".join(cleaned) if cleaned else None

