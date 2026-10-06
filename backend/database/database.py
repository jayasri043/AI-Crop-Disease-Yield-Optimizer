from pathlib import Path
import sqlite3


DATABASE_PATH = Path("backend/database/crop_history.db")


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )
    connection.row_factory = sqlite3.Row

    # Helps reduce SQLite locking during normal frontend/backend usage
    connection.execute("PRAGMA journal_mode=WAL")

    return connection


def initialize_database():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT NOT NULL,
            disease TEXT NOT NULL,
            confidence REAL NOT NULL,

            severity TEXT,
            affected_area REAL,

            risk_level TEXT,
            risk_score REAL,

            treatment_priority TEXT,
            treatment_priority_score REAL,

            temperature REAL,
            humidity REAL,
            rainfall REAL,

            location TEXT,

            base_yield REAL,
            yield_loss_percentage REAL,
            adjusted_yield REAL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


# ==========================================
# Save scan history
# ==========================================

def save_scan_history(
    crop,
    disease,
    confidence,
    severity,
    affected_area,
    risk_level,
    risk_score,
    treatment_priority,
    treatment_priority_score,
    temperature,
    humidity,
    rainfall,
    location,
    base_yield,
    yield_loss_percentage,
    adjusted_yield
):

    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO scan_history (
                crop,
                disease,
                confidence,
                severity,
                affected_area,
                risk_level,
                risk_score,
                treatment_priority,
                treatment_priority_score,
                temperature,
                humidity,
                rainfall,
                location,
                base_yield,
                yield_loss_percentage,
                adjusted_yield
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                crop,
                disease,
                confidence,
                severity,
                affected_area,
                risk_level,
                risk_score,
                treatment_priority,
                treatment_priority_score,
                temperature,
                humidity,
                rainfall,
                location,
                base_yield,
                yield_loss_percentage,
                adjusted_yield
            )
        )

        connection.commit()

    finally:
        connection.close()


# ==========================================
# Get scan history
# ==========================================

def get_scan_history():

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                crop,
                disease,
                confidence,
                severity,
                affected_area,
                risk_level,
                risk_score,
                treatment_priority,
                treatment_priority_score,
                temperature,
                humidity,
                rainfall,
                location,
                base_yield,
                yield_loss_percentage,
                adjusted_yield,
                created_at
            FROM scan_history
            ORDER BY id DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]

    finally:
        connection.close()