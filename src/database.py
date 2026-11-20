"""SQLite persistence for prediction history (stored locally, no personal identifiers)."""
from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.config import DB_PATH

COLUMNS = ["study_hours", "attendance", "previous_marks", "assignment_completion", "sleep_hours"]

_SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    study_hours REAL NOT NULL,
    attendance REAL NOT NULL,
    previous_marks REAL NOT NULL,
    assignment_completion REAL NOT NULL,
    sleep_hours REAL NOT NULL,
    predicted_score REAL NOT NULL,
    category TEXT NOT NULL
)
"""


def _connect(db_path) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(_SCHEMA)
    return conn


def save_prediction(inputs: dict, score: float, category: str, db_path=DB_PATH) -> int:
    with closing(_connect(db_path)) as conn, conn:
        cur = conn.execute(
            "INSERT INTO predictions (created_at, study_hours, attendance, previous_marks, "
            "assignment_completion, sleep_hours, predicted_score, category) VALUES (?,?,?,?,?,?,?,?)",
            (datetime.now().isoformat(timespec="seconds"), *[float(inputs[c]) for c in COLUMNS],
             float(score), category),
        )
        return cur.lastrowid


def get_predictions(db_path=DB_PATH) -> pd.DataFrame:
    with closing(_connect(db_path)) as conn:
        df = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC", conn)
    return df


def delete_prediction(pred_id: int, db_path=DB_PATH) -> None:
    with closing(_connect(db_path)) as conn, conn:
        conn.execute("DELETE FROM predictions WHERE id = ?", (int(pred_id),))


def delete_all(db_path=DB_PATH) -> None:
    with closing(_connect(db_path)) as conn, conn:
        conn.execute("DELETE FROM predictions")
