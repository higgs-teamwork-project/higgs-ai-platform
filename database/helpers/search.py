from typing import Iterable

from .. import dataset_db


def find_ngos_by_sector(sector: str) -> list:
    """
    Return NGOs where the sectors text contains the given sector string (case-insensitive).
    """
    pattern = f"%{sector}%"
    conn = dataset_db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM ngos WHERE LOWER(sectors) LIKE LOWER(?) ORDER BY id",
            (pattern,),
        )
        return cur.fetchall()
    finally:
        conn.close()


def find_ngos_by_region(region: str) -> list:
    """
    Return NGOs where the regions text contains the given region string (case-insensitive).
    """
    pattern = f"%{region}%"
    conn = dataset_db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM ngos WHERE LOWER(regions) LIKE LOWER(?) ORDER BY id",
            (pattern,),
        )
        return cur.fetchall()
    finally:
        conn.close()


def find_ngos_by_sectors_any(sectors: Iterable[str]) -> list:
    """
    Return NGOs that match any of the provided sectors.
    """
    sectors = [s for s in sectors if s]
    if not sectors:
        return []

    # Build OR conditions like: LOWER(sectors) LIKE ? OR LOWER(sectors) LIKE ?
    conditions = " OR ".join("LOWER(sectors) LIKE LOWER(?)" for _ in sectors)
    patterns = [f"%{s}%" for s in sectors]

    conn = dataset_db.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM ngos WHERE {conditions} ORDER BY id",
            patterns,
        )
        return cur.fetchall()
    finally:
        conn.close()

