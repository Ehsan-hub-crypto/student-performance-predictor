"""Input validation, dataset loading/cleaning and the train/test split."""
from __future__ import annotations

import math
from typing import Mapping

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import RANDOM_STATE, TEST_SIZE

FEATURES = [
    "study_hours",
    "attendance",
    "previous_marks",
    "assignment_completion",
    "sleep_hours",
]
TARGET = "final_score"

# Human-readable labels and the valid (min, max) range of each input.
LABELS = {
    "study_hours": "Study hours / day",
    "attendance": "Attendance (%)",
    "previous_marks": "Previous marks",
    "assignment_completion": "Assignments (%)",
    "sleep_hours": "Sleep hours / day",
}
LIMITS = {
    "study_hours": (0.0, 12.0),
    "attendance": (0.0, 100.0),
    "previous_marks": (0.0, 100.0),
    "assignment_completion": (0.0, 100.0),
    "sleep_hours": (0.0, 12.0),
}


class ValidationError(ValueError):
    """Raised when user input is missing, non-numeric or out of range."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_input(data: Mapping[str, object]) -> dict[str, float]:
    """Return cleaned float inputs, or raise ValidationError listing every problem."""
    errors: list[str] = []
    clean: dict[str, float] = {}
    for name in FEATURES:
        label = LABELS[name]
        raw = data.get(name)
        if raw is None or (isinstance(raw, str) and not raw.strip()):
            errors.append(f"{label}: please enter a value.")
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError):
            errors.append(f"{label}: '{raw}' is not a number.")
            continue
        if math.isnan(value) or math.isinf(value):
            errors.append(f"{label}: value must be a real number.")
            continue
        lo, hi = LIMITS[name]
        if not lo <= value <= hi:
            errors.append(f"{label}: must be between {lo:g} and {hi:g} (you entered {value:g}).")
            continue
        clean[name] = value
    if errors:
        raise ValidationError(errors)
    return clean


def to_frame(clean: Mapping[str, float]) -> pd.DataFrame:
    """Single-row DataFrame in the exact column order used for training."""
    return pd.DataFrame([[clean[f] for f in FEATURES]], columns=FEATURES)


def load_dataset(path) -> pd.DataFrame:
    """Read the CSV and check that all required columns exist."""
    df = pd.read_csv(path)
    missing = [c for c in FEATURES + [TARGET] if c not in df.columns]
    if missing:
        raise ValueError(f"Dataset is missing columns: {missing}")
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing values, duplicates and out-of-range values."""
    df = df[FEATURES + [TARGET]].apply(pd.to_numeric, errors="coerce").dropna().drop_duplicates()
    for name, (lo, hi) in LIMITS.items():
        df = df[df[name].between(lo, hi)]
    return df[df[TARGET].between(0, 100)].reset_index(drop=True)


def split_data(df: pd.DataFrame):
    """Hold out a test set the model never sees during training."""
    return train_test_split(df, test_size=TEST_SIZE, random_state=RANDOM_STATE)
