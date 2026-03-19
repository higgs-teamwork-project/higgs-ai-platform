from pathlib import Path
import os
import sqlite3
from datetime import datetime, time, date, timedelta
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "schedule.db"

def get_connection() -> sqlite3.Connection:
    """
    Connection to the accounts database (emails + password hashes).
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_schema() -> None:
    """
    Create the schedule table if it does not exist
    Fields:
    - donor_id: id of donor for whom meeting is set
    - ngo_id: id of ngo for whom meeting is set
    - meeting_time: timestamp, of meeting
    """
    conn = get_connection()

    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER AUTOINCREMENT,
                donor_id INTEGER NOT NULL,
                ngo_id INTEGER NOT NULL,
                meeting_time TIMESTAMP,
                PRIMARY KEY (donor_id, ngo_id)
            );
            """
        )
    finally:
        conn.close()


def insert_meeting(
    donor_id: int,
    ngo_id: int,
    timestamp: datetime
) -> None:
    """
    Insert or update meeting time for specific ngo and specfic donor
    """
    conn = get_connection()

    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO schedule(donor_id, ngo_id, meeting_time)
            VALUES(?, ?, ?)
            ON CONFLICT(donor_id, ngo_id)
            DO UPDATE SET meeting_time=excluded.meeting_time;
            """,
            (
                donor_id,
                ngo_id,
                timestamp,
            ),
        )

    finally:
        conn.close()

def get_donor_meetings(donor_id: int) -> list[sqlite3.Row]:
    """
    Get meetings for specific donor
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * 
            FROM schedule
            WHERE donor_id = ?
            """,
            (donor_id,)
        )
        return cur.fetchall()
    finally:
        conn.close()

def get_ngo_meetings(ngo_id: int) -> list[sqlite3.Row]:
    """
    Get meetings for specific ngo
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * 
            FROM schedule
            WHERE ngo_id = ?
            """,
            (ngo_id,)
        )
        return cur.fetchall()
    finally:
        conn.close()

def get_donor_ngo_meeting(
    donor_id: int, 
    ngo_id: int
) -> Optional[sqlite3.Row]:
    """
    Get meeting between specific donor and ngo
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * 
            FROM schedule
            WHERE donor_id = ? AND ngo_id = ?
            """,
            (donor_id, ngo_id,)
        )
        return cur.fetchone()
    finally:
        conn.close()