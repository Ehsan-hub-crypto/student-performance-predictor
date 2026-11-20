"""Sidebar: model status, configurable category thresholds and data-storage notice."""
from __future__ import annotations

import streamlit as st

from src.config import APP_NAME, DEFAULT_THRESHOLDS, LOGO_PATH


def _reset_thresholds() -> None:
    for key, val in DEFAULT_THRESHOLDS.items():
        st.session_state[f"thr_{key}"] = val


def render_sidebar(bundle: dict | None, load_error: str | None) -> dict:
    """Draw the sidebar and return the active category thresholds."""
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=64)
        st.markdown(f"### {APP_NAME}")

        st.markdown("**Model status**")
        if bundle:
            st.success("Model loaded", icon="✅")
            st.caption(f"{bundle['model_name']} · trained {bundle['trained_at'][:10]}")
        else:
            st.error("Model unavailable", icon="⚠️")
            st.caption(load_error or "")

        st.markdown("---")
        st.markdown("**Category thresholds**")
        st.caption("Minimum predicted score for each band. Categories are indicative labels, not official grades.")
        for key, default in DEFAULT_THRESHOLDS.items():
            st.session_state.setdefault(f"thr_{key}", default)
        exc = st.number_input("Excellent from", 0.0, 100.0, step=1.0, key="thr_Excellent")
        good = st.number_input("Good from", 0.0, 100.0, step=1.0, key="thr_Good")
        avg = st.number_input("Average from", 0.0, 100.0, step=1.0, key="thr_Average")
        st.button("Reset thresholds", on_click=_reset_thresholds, use_container_width=True)
        valid = exc > good > avg
        if not valid:
            st.warning("Thresholds must satisfy Excellent > Good > Average. Using defaults until fixed.")

        st.markdown("---")
        st.markdown("**Your data**")
        st.caption(
            "Predictions you choose to save are stored only in a local SQLite file on the machine running this app "
            "(`data/predictions.db`). No name, email or other personal details are collected, and nothing is sent anywhere."
        )
    return {"Excellent": exc, "Good": good, "Average": avg} if valid else dict(DEFAULT_THRESHOLDS)
