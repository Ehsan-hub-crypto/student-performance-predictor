"""Turn a student's inputs (and the model's what-if results) into plain-language recommendations.

Every recommendation carries a ``kind`` so the UI can show where the advice comes from:

* ``evidence`` - consistent with published educational / sleep research (general findings about
  groups of students, not a guarantee for any individual).
* ``general``  - common-sense study advice that is reasonable but not specifically validated.
* ``model``    - calculated by this app's model from its training data (patterns, not causes).
* ``strength`` - something that is already going well.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

KIND_LABELS = {
    "evidence": "Evidence-informed",
    "general": "General tip",
    "model": "Model what-if",
    "strength": "Going well",
}

KIND_EXPLANATIONS = {
    "evidence": (
        "Consistent with published research on students or sleep. These are findings about "
        "groups, so they show a tendency, not a guarantee for any one person."
    ),
    "general": "Sensible study advice that is not specifically backed by a research study.",
    "model": (
        "Calculated by this app's model from its training data. It shows patterns the model "
        "learned, not proof of cause and effect."
    ),
}

MIN_MODEL_GAIN = 0.5  # ignore what-if changes smaller than half a mark (within model noise)
MAX_MODEL_ITEMS = 2


def build_recommendations(
    inputs: Mapping[str, float], what_if: Sequence[Mapping[str, Any]] | None = None
) -> list[dict[str, str]]:
    """Return recommendations ordered as: things to work on, model what-ifs, strengths."""
    attendance = inputs["attendance"]
    study = inputs["study_hours"]
    assignments = inputs["assignment_completion"]
    sleep = inputs["sleep_hours"]
    previous = inputs["previous_marks"]

    work_on: list[dict[str, str]] = []
    strengths: list[dict[str, str]] = []

    def add(bucket: list[dict[str, str]], kind: str, title: str, detail: str) -> None:
        bucket.append({"kind": kind, "title": title, "detail": detail})

    # Attendance
    if attendance < 75:
        add(
            work_on,
            "evidence",
            "Improve your attendance",
            f"You attend about {attendance:g}% of classes. In educational research, regular "
            "attendance is consistently associated with better grades (an association, not a "
            "guarantee). Many institutions also set a minimum requirement, so check yours. "
            "Protect your class time and catch up quickly on anything you miss.",
        )
    elif attendance >= 90:
        add(strengths, "strength", "Strong attendance", f"At {attendance:g}%, you show up consistently. Keep it up.")

    # Study time
    if study < 2:
        add(
            work_on,
            "general",
            "Increase focused study time",
            f"You study about {study:g} h a day outside class. Try adding 30-45 minutes of "
            "distraction-free study and build up gradually instead of all at once.",
        )
    elif study > 8:
        add(
            work_on,
            "evidence",
            "Balance very long study days",
            f"{study:g} h a day is a lot. Learning research suggests that shorter, spaced sessions "
            "with breaks usually work better than marathon sessions, so more hours do not always "
            "mean more progress.",
        )
    else:
        add(
            work_on,
            "evidence",
            "Make your study time count",
            "Testing yourself (practice questions, flashcards, past papers) and spreading revision "
            "over several days are among the study techniques best supported by learning research.",
        )
        if study >= 3:
            add(strengths, "strength", "Regular study time", f"Around {study:g} h of daily self-study is a solid routine.")

    # Assignments
    if assignments < 70:
        add(
            work_on,
            "general",
            "Complete assignments regularly",
            f"You complete about {assignments:g}% of assignments. Assignments are built-in practice, "
            "and finishing them steadily avoids last-minute pile-ups. A weekly planner with small "
            "daily targets can help.",
        )
    elif assignments >= 90:
        add(strengths, "strength", "Consistent with assignments", f"Completing about {assignments:g}% of assignments is excellent practice.")

    # Sleep
    if sleep < 7:
        add(
            work_on,
            "evidence",
            "Maintain a healthy sleep schedule",
            f"You sleep about {sleep:g} h a night. Sleep-medicine guidance recommends at least 7 hours "
            "for adults (teenagers typically need more), and short sleep is linked with poorer "
            "attention and memory. A regular bedtime and wake-up time is a good place to start.",
        )
    elif sleep > 9.5:
        add(
            work_on,
            "general",
            "Review your sleep routine",
            f"Sleeping about {sleep:g} h a night is longer than typical. If you often still feel tired, "
            "a consistent schedule can help, and if it continues, consider speaking to a health "
            "professional.",
        )
    elif sleep <= 9:
        add(strengths, "strength", "Healthy sleep range", f"{sleep:g} h a night is within the commonly recommended range for adults.")

    # Previous marks
    if previous < 50:
        add(
            work_on,
            "general",
            "Strengthen your foundations",
            f"Your previous marks ({previous:g}/100) point to some gaps. List the topics where you lost "
            "the most marks and ask teachers or classmates for help early, since topics tend to build "
            "on each other.",
        )
    elif previous >= 75:
        add(strengths, "strength", "Solid academic base", f"Previous marks of {previous:g}/100 give you a strong starting point.")

    # Model-based what-ifs (already sorted best-first by predict.what_if)
    model_items: list[dict[str, str]] = []
    for item in (what_if or []):
        if item["delta"] >= MIN_MODEL_GAIN and len(model_items) < MAX_MODEL_ITEMS:
            add(
                model_items,
                "model",
                f"Model what-if: {item['label']}",
                f"In this model, that change would shift your predicted score by about "
                f"{item['delta']:+.1f} marks, with everything else unchanged. It reflects patterns in "
                "the training data, not a guaranteed result.",
            )

    return work_on + model_items + strengths
