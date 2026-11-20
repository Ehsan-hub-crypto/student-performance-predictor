"""Generate a SYNTHETIC student dataset (no real students are involved).

Why synthetic? Real student records are private and not bundled with this repo. The
relationships below are plausible assumptions written by the project author, NOT
findings from real research. To use real data, replace data/student_data.csv with a CSV
that has the same columns and run `python -m src.train`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import DATA_PATH, RANDOM_STATE


def generate(n: int = 2000, seed: int = RANDOM_STATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    diligence = rng.normal(0, 1, n)  # hidden trait that loosely links the habits

    study = np.clip(rng.normal(4.0, 1.9, n) + 0.8 * diligence, 0, 12)
    attendance = np.clip(rng.normal(78, 12, n) + 5 * diligence, 30, 100)
    previous = np.clip(rng.normal(62, 14, n) + 5 * diligence, 10, 100)
    assignment = np.clip(rng.normal(72, 15, n) + 6 * diligence, 10, 100)
    sleep = np.clip(rng.normal(6.8, 1.1, n), 3, 10)

    final = (
        8
        + 0.50 * previous
        + 0.12 * attendance
        + 0.10 * assignment
        + 14 * (1 - np.exp(-study / 3))  # diminishing returns on study time
        - 0.8 * (sleep - 7.5) ** 2  # too little or too much sleep hurts a bit
        + rng.normal(0, 4, n)
    )
    return pd.DataFrame(
        {
            "study_hours": study.round(1),
            "attendance": attendance.round(1),
            "previous_marks": previous.round(1),
            "assignment_completion": assignment.round(1),
            "sleep_hours": sleep.round(1),
            "final_score": np.clip(final, 0, 100).round(1),
        }
    )


if __name__ == "__main__":
    if DATA_PATH.exists():
        print(f"{DATA_PATH} already exists - not overwriting. Delete it first to regenerate.")
    else:
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(DATA_PATH, index=False)
        print(f"Wrote synthetic dataset to {DATA_PATH}")
