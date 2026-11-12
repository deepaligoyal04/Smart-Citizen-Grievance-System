import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).parent / "grievance.db"
DATA_PATH = Path(__file__).parent / "data" / "citizen_grievances.csv"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS grievances (
                complaint_id TEXT PRIMARY KEY,
                citizen_name TEXT NOT NULL,
                category TEXT NOT NULL,
                department TEXT NOT NULL,
                description TEXT NOT NULL,
                area TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                submitted_date TEXT NOT NULL,
                resolved_date TEXT,
                resolution_days INTEGER
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM grievances").fetchone()[0]
        if count == 0 and DATA_PATH.exists():
            sample = pd.read_csv(DATA_PATH).fillna("")
            sample.to_sql("grievances", conn, if_exists="append", index=False)

def fetch_grievances():
    with get_connection() as conn:
        return pd.read_sql_query(
            "SELECT * FROM grievances ORDER BY submitted_date DESC", conn
        )

def insert_grievance(record):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO grievances
            (complaint_id, citizen_name, category, department, description, area,
             priority, status, submitted_date, resolved_date, resolution_days)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, record)

def update_status(complaint_id, status):
    with get_connection() as conn:
        if status == "Resolved":
            conn.execute("""
                UPDATE grievances
                SET status=?, resolved_date=DATE('now'),
                    resolution_days=CAST(julianday(DATE('now')) -
                    julianday(submitted_date) AS INTEGER)
                WHERE complaint_id=?
            """, (status, complaint_id))
        else:
            conn.execute("""
                UPDATE grievances SET status=?, resolved_date=NULL,
                resolution_days=NULL WHERE complaint_id=?
            """, (status, complaint_id))
