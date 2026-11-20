"""Prediction result dashboard: score, category, breakdown charts, recommendations."""
from __future__ import annotations

import streamlit as st

from components import charts
from components.styles import html
from src.config import CATEGORIES
from src.predict import categorize, recommendations


def render_results(result: dict, bundle: dict, thresholds: dict) -> None:
    score, inputs = result["score"], result["inputs"]
    category = categorize(score, thresholds)
    result["category"] = category

    st.markdown("## Your results")
    for w in result.get("warnings", []):
        st.warning(w, icon="⚠️")

    c1, c2 = st.columns([1, 1.4], gap="large")
    with c1:
        html(f"""
        <div class="score-card">
        <div class="eyebrow">Predicted score</div>
        <div class="num">{score:.1f}</div>
        <div class="of">out of 100</div>
        <div style="margin-top:.9rem"><span class="pill">{category}</span></div>
        </div>
        """)
        st.plotly_chart(charts.gauge(score), use_container_width=True, config={"displayModeBar": False})
    with c2:
        mae = bundle["metrics"]["Random Forest"]["mae"]
        r2 = bundle["metrics"]["Random Forest"]["r2"]
        html(f"""
        <div class="card">
        <h4>How to read this</h4>
        <p>The model estimates your score would be around <b style="color:#F0D77A">{score:.1f}</b>.
        On held-out test data its average error was about <b>±{mae:.1f} marks</b>, so treat it as a range
        ({max(0, score - mae):.0f}-{min(100, score + mae):.0f}), not an exact number.</p>
        <p style="margin-top:.7rem">Category bands: Excellent ≥ {thresholds['Excellent']:g},
        Good ≥ {thresholds['Good']:g}, Average ≥ {thresholds['Average']:g}, otherwise Needs Improvement.
        Categories are <b>indicative</b> and can be changed in the sidebar.</p>
        </div>
        """)
        m1, m2 = st.columns(2)
        m1.metric("Test MAE", f"{mae:.2f}", help="Mean absolute error on the held-out test set (lower is better).")
        m2.metric("Test R²", f"{r2:.3f}", help="Share of score variation explained on the test set (closer to 1 is better).")
        if bundle.get("data_source") == "synthetic":
            st.caption("Metrics measure how well the model learned a **synthetic** dataset - not real-world accuracy.")

    st.markdown("### Performance breakdown")
    b1, b2 = st.columns(2, gap="large")
    b1.plotly_chart(charts.breakdown(inputs), use_container_width=True, config={"displayModeBar": False})
    b2.plotly_chart(charts.radar(inputs), use_container_width=True, config={"displayModeBar": False})

    st.markdown("### Personalized recommendations")
    html("""<div class="note"><b>Research-backed</b> tips cite a published source. <b>General</b> tips are common
    study advice that is not proven for every student. All tips are rule-based, written by hand - they are not
    produced by the ML model.</div>""")
    st.write("")
    recs = recommendations(inputs)
    cols = st.columns(2, gap="medium")
    for i, rec in enumerate(recs):
        tag = '<span class="pill">Research-backed</span>' if rec["kind"] == "research" else '<span class="pill gen">General</span>'
        source = f'<p style="margin-top:.5rem;font-size:.8rem">Source: {rec["source"]}</p>' if rec.get("source") else ""
        with cols[i % 2]:
            html(f'<div class="card"><div>{tag}</div><h4 style="margin-top:.6rem">{rec["title"]}</h4><p>{rec["text"]}</p>{source}</div>')
            st.write("")
