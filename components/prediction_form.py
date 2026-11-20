"""The student input form: 4 sliders + 1 number input, with clear and predict buttons."""
from __future__ import annotations

import streamlit as st

DEFAULTS = {"f_study": 4.0, "f_attendance": 75, "f_previous": None, "f_assignment": 70, "f_sleep": 7.0}


def _clear_all() -> None:
    for key, val in DEFAULTS.items():
        st.session_state[key] = val
    st.session_state.pop("result", None)
    st.session_state.pop("form_errors", None)


def render_form(disabled: bool = False) -> dict | None:
    """Return the raw input dict when 'Predict' is pressed, otherwise None."""
    for key, val in DEFAULTS.items():
        st.session_state.setdefault(key, val)

    with st.form("prediction_form", border=True):
        left, right = st.columns(2, gap="large")
        with left:
            study = st.slider("Study hours per day", 0.0, 12.0, step=0.5, key="f_study",
                              help="Self-study time on an average day.")
            st.markdown('<div class="hint">How many hours do you study daily, excluding classroom time?</div>',
                        unsafe_allow_html=True)
            attendance = st.slider("Attendance percentage (%)", 0, 100, key="f_attendance",
                                   help="Classes attended divided by total classes held.")
            st.markdown('<div class="hint">What share of your scheduled classes do you attend?</div>',
                        unsafe_allow_html=True)
            sleep = st.slider("Average sleep hours per night", 0.0, 12.0, step=0.5, key="f_sleep",
                              help="Typical nightly sleep, including weekends.")
            st.markdown('<div class="hint">On average, how many hours do you sleep each night?</div>',
                        unsafe_allow_html=True)
        with right:
            previous = st.number_input("Previous academic marks (0-100)", min_value=0.0, max_value=100.0,
                                       step=1.0, value=None, key="f_previous", placeholder="e.g. 68",
                                       help="Your most recent overall result, as a percentage.")
            st.markdown('<div class="hint">Your latest overall score out of 100 (for example last semester).</div>',
                        unsafe_allow_html=True)
            assignment = st.slider("Assignment completion (%)", 0, 100, key="f_assignment",
                                   help="Assignments submitted divided by assignments given.")
            st.markdown('<div class="hint">What percentage of assignments do you complete and submit on time?</div>',
                        unsafe_allow_html=True)

        b1, b2, _ = st.columns([1, 1.4, 2])
        b1.form_submit_button("Clear All", on_click=_clear_all, use_container_width=True, disabled=disabled)
        submitted = b2.form_submit_button("Predict My Performance", type="primary", use_container_width=True,
                                          disabled=disabled)

    if submitted:
        return {"study_hours": study, "attendance": attendance, "previous_marks": previous,
                "assignment_completion": assignment, "sleep_hours": sleep}
    return None
