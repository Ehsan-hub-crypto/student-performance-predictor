"""Load the trained model, predict, categorise and generate recommendations."""
from __future__ import annotations

from typing import Mapping

import joblib
import numpy as np

from src.config import CATEGORIES, DEFAULT_THRESHOLDS, MODEL_PATH
from src.preprocess import LABELS, to_frame, validate_input


class ModelUnavailableError(RuntimeError):
    """Raised when the trained model file is missing or cannot be loaded."""


def load_bundle(path=MODEL_PATH) -> dict:
    try:
        return joblib.load(path)
    except FileNotFoundError as exc:
        raise ModelUnavailableError(
            "Model file not found. Run `python -m src.train` once to train and save the model."
        ) from exc
    except Exception as exc:  # corrupted file, version mismatch...
        raise ModelUnavailableError(
            f"The model file could not be loaded ({exc.__class__.__name__}). "
            "Re-run `python -m src.train` to rebuild it."
        ) from exc


def predict_score(inputs: Mapping[str, object], bundle: dict | None = None) -> dict:
    """Validate inputs, run the model and return score + any out-of-range warnings."""
    clean = validate_input(inputs)
    bundle = bundle or load_bundle()
    raw = float(bundle["model"].predict(to_frame(clean))[0])
    score = float(np.clip(raw, 0, 100))

    warnings = []
    for name, (lo, hi) in bundle.get("feature_ranges", {}).items():
        if not lo <= clean[name] <= hi:
            warnings.append(
                f"{LABELS[name]} = {clean[name]:g} is outside the range the model learned from "
                f"({lo:g}-{hi:g}), so this estimate is less reliable."
            )
    return {"score": round(score, 1), "inputs": clean, "warnings": warnings}


def categorize(score: float, thresholds: Mapping[str, float] | None = None) -> str:
    t = thresholds or DEFAULT_THRESHOLDS
    if score >= t["Excellent"]:
        return CATEGORIES[0]
    if score >= t["Good"]:
        return CATEGORIES[1]
    if score >= t["Average"]:
        return CATEGORIES[2]
    return CATEGORIES[3]


def recommendations(inputs: Mapping[str, float]) -> list[dict]:
    """Rule-based tips. `kind` is 'research' (broadly supported) or 'general' (common advice).

    These rules are written by hand; they are NOT learned by the ML model.
    """
    r: list[dict] = []
    study, att = inputs["study_hours"], inputs["attendance"]
    prev, asg, sleep = inputs["previous_marks"], inputs["assignment_completion"], inputs["sleep_hours"]

    if att < 75:
        r.append(dict(kind="general", title="Improve attendance",
                      text=f"Your attendance is {att:g}%. Many institutions require around 75% - check your own "
                           "rules, and try to attend every class for the next few weeks."))
    if study < 2:
        r.append(dict(kind="research", title="Build up focused study time",
                      text="Increase study time gradually (for example +30 minutes a week) and use short, focused "
                           "sessions. Spaced practice and self-testing are among the best-supported study methods.",
                      source="Dunlosky et al. (2013), Psychological Science in the Public Interest"))
    elif study > 8:
        r.append(dict(kind="general", title="Protect quality over quantity",
                      text="Very long study days often bring diminishing returns. Add breaks and make sure "
                           "you keep time for sleep and revision."))
    else:
        r.append(dict(kind="research", title="Make study time count",
                      text="Mix in self-testing (practice questions, recalling without notes) and spread topics "
                           "across several days rather than cramming.",
                      source="Dunlosky et al. (2013), Psychological Science in the Public Interest"))
    if asg < 70:
        r.append(dict(kind="general", title="Complete assignments regularly",
                      text=f"You complete about {asg:g}% of assignments. Break each one into small tasks and "
                           "schedule fixed slots in your week."))
    if sleep < 6:
        r.append(dict(kind="research", title="Maintain a healthy sleep schedule",
                      text="You sleep under 6 hours on average. Sleep-medicine consensus recommends at least "
                           "7 hours for adults; a consistent bedtime helps.",
                      source="Watson et al. (2015), AASM & Sleep Research Society consensus statement"))
    elif sleep > 9:
        r.append(dict(kind="general", title="Keep a consistent sleep routine",
                      text="Sleeping over 9 hours regularly can signal an irregular schedule. Aim for steady "
                           "wake-up and bedtime hours."))
    if prev < 50:
        r.append(dict(kind="general", title="Revisit the fundamentals",
                      text="Your previous marks suggest some gaps. Identify the weakest topics and ask a teacher "
                           "or peer group for help early."))
    if not r or (len(r) == 1 and r[0]["title"] == "Make study time count"):
        r.insert(0, dict(kind="general", title="Keep your routine",
                         text="Your habits look balanced. Stay consistent and review your progress regularly."))
    return r
