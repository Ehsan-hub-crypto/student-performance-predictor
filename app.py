"""EduPredict AI - Streamlit entry point.   Run with:  streamlit run app.py"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components import charts
from components.prediction_form import render_form
from components.results import render_results
from components.sidebar import render_sidebar
from components.styles import html, inject_css
from src import database
from src.config import APP_NAME, CATEGORIES, GITHUB_URL, LOGO_PATH
from src.predict import ModelUnavailableError, categorize, load_bundle, predict_score
from src.preprocess import LABELS, ValidationError

PAGES = ["Home", "Predict Performance", "Analytics", "About Project"]

st.set_page_config(page_title=f"{APP_NAME} - Student Performance Predictor",
                   page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🎓", layout="wide")
inject_css()


@st.cache_resource(show_spinner=False)
def get_bundle() -> dict:
    return load_bundle()


def go(page: str) -> None:
    """Button callback that switches page (callbacks may set the nav widget's state)."""
    st.session_state["page"] = page


# ------------------------------------------------------------------ model + sidebar
try:
    BUNDLE, LOAD_ERROR = get_bundle(), None
except ModelUnavailableError as exc:
    BUNDLE, LOAD_ERROR = None, str(exc)
THRESHOLDS = render_sidebar(BUNDLE, LOAD_ERROR)

# ------------------------------------------------------------------ top navigation
st.session_state.setdefault("page", "Home")
n1, n2, n3, n4 = st.columns([1.5, 4.4, 0.45, 1.2], vertical_alignment="center")
n1.markdown('<div class="brand"><span class="dot">E</span>EduPredict <b>AI</b></div>', unsafe_allow_html=True)
n2.radio("Navigation", PAGES, key="page", horizontal=True, label_visibility="collapsed")
n3.markdown(
    f'<a class="gh" href="{GITHUB_URL}" target="_blank" rel="noopener" title="View on GitHub" aria-label="GitHub">'
    '<svg viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 '
    '0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 '
    '1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15'
    '-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82'
    '.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2'
    ' 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"/></svg></a>', unsafe_allow_html=True)
n4.button("Predict Now", type="primary", on_click=go, args=("Predict Performance",), use_container_width=True,
          key="cta_nav")
st.markdown('<hr class="nav">', unsafe_allow_html=True)


# ------------------------------------------------------------------ pages
def page_home() -> None:
    left, right = st.columns([1.25, 1], gap="large", vertical_alignment="center")
    with left:
        html("""
        <div class="hero">
        <div class="eyebrow">Student performance predictor</div>
        <div class="h1">Predict Your Academic Future <span>with AI</span></div>
        <p class="sub">Understand your academic potential through intelligent machine learning predictions
        and personalized performance insights.</p>
        </div>
        """)
        b1, b2, _ = st.columns([1.2, 1.2, 1])
        b1.button("Start Prediction", type="primary", on_click=go, args=("Predict Performance",),
                  use_container_width=True, key="hero_predict")
        b2.button("Explore Analytics", on_click=go, args=("Analytics",), use_container_width=True, key="hero_analytics")
    with right:
        html("""
        <div class="orb"><div class="ring"></div><div class="ring"></div><div class="ring"></div>
        <div class="core">AI</div></div>
        """)

    st.write("")
    s1, s2, s3 = st.columns(3, gap="medium")
    for col, (t, d) in zip((s1, s2, s3), [
        ("AI-powered predictions", "A Random Forest model trained with scikit-learn."),
        ("Data-driven insights", "Charts and tips based on the five habits you enter."),
        ("Instant performance analysis", "Results appear the moment you press Predict."),
    ]):
        col.markdown(f'<div class="card"><h4 style="color:#F0D77A">{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)

    st.write("")
    st.markdown("### How it works")
    html("""
    <div class="flow">
    <div class="step">1. Enter your habits<small>5 simple inputs</small></div><div class="arrow">→</div>
    <div class="step">2. Model predicts<small>Random Forest regression</small></div><div class="arrow">→</div>
    <div class="step">3. Get insights<small>Score, charts, tips</small></div>
    </div>
    """)
    st.write("")
    html("""<div class="note">Predictions are estimates, not guaranteed academic outcomes. The bundled demo model is
    trained on <b>synthetic</b> data - see the About page for details.</div>""")


def page_predict() -> None:
    st.markdown("## Predict your performance")
    st.markdown('<p class="muted">Answer five quick questions. Nothing is saved unless you choose to save the result.</p>',
                unsafe_allow_html=True)

    if BUNDLE is None:
        st.error("**The prediction model is not set up yet.** No predictions can be shown until it exists.", icon="🛠️")
        st.code("pip install -r requirements.txt\npython -m src.train", language="bash")
        st.caption(LOAD_ERROR or "")
        render_form(disabled=True)
        return

    raw = render_form()
    if raw is not None:
        try:
            with st.spinner("Analysing your inputs..."):
                st.session_state["result"] = predict_score(raw, BUNDLE)
            st.session_state.pop("form_errors", None)
            st.session_state.pop("saved_msg", None)
        except ValidationError as exc:
            st.session_state["form_errors"] = exc.errors
            st.session_state.pop("result", None)
        except ModelUnavailableError as exc:
            st.session_state["form_errors"] = [str(exc)]

    for err in st.session_state.get("form_errors", []):
        st.error(err, icon="🚫")

    result = st.session_state.get("result")
    if result:
        render_results(result, BUNDLE, THRESHOLDS)
        st.write("")
        a, b, _ = st.columns([1.3, 1.3, 2])
        if a.button("Save this prediction", use_container_width=True, key="save_pred"):
            database.save_prediction(result["inputs"], result["score"], result["category"])
            st.session_state["saved_msg"] = "Saved. See it on the Analytics page."
        b.button("View analytics", on_click=go, args=("Analytics",), use_container_width=True, key="to_analytics")
        if st.session_state.get("saved_msg"):
            st.success(st.session_state["saved_msg"])


def _fmt(row) -> str:
    created_at = str(row["created_at"])
    if len(created_at) >= 16:
        created_at = created_at[:16].replace("T", " ")
    return f"#{int(row['id'])} · {created_at} · {row['predicted_score']:.1f}"


def page_analytics() -> None:
    st.markdown("## Analytics")
    st.markdown('<p class="muted">Based only on the predictions you saved on this device.</p>', unsafe_allow_html=True)
    df = database.get_predictions()

    if df.empty:
        html("""<div class="card" style="text-align:center;padding:2.5rem 1rem">
        <h4>No saved predictions yet</h4>
        <p>Make a prediction and press <b>Save this prediction</b> - your analytics will appear here.</p></div>""")
        st.write("")
        st.button("Make a prediction", type="primary", on_click=go, args=("Predict Performance",), key="empty_cta")
        return

    df["category"] = df["predicted_score"].apply(lambda s: categorize(s, THRESHOLDS))
    top = df["category"].value_counts().idxmax()
    k1, k2, k3 = st.columns(3)
    for col, label, val in [(k1, "Total predictions", str(len(df))), (k2, "Average predicted score", f"{df['predicted_score'].mean():.1f}"),
                            (k3, "Most common category", top)]:
        col.markdown(f'<div class="kpi"><div class="l">{label}</div><div class="v">{val}</div></div>', unsafe_allow_html=True)
    st.write("")

    c1, c2 = st.columns(2, gap="medium")
    c1.plotly_chart(charts.category_distribution(df, CATEGORIES), use_container_width=True, config={"displayModeBar": False})
    c2.plotly_chart(charts.history_line(df), use_container_width=True, config={"displayModeBar": False})
    c3, c4 = st.columns(2, gap="medium")
    c3.plotly_chart(charts.scatter(df, "study_hours", "Study hours vs predicted marks", "Study hours / day"),
                    use_container_width=True, config={"displayModeBar": False})
    c4.plotly_chart(charts.scatter(df, "attendance", "Attendance vs predicted marks", "Attendance (%)"),
                    use_container_width=True, config={"displayModeBar": False})
    if len(df) < 3:
        st.caption("Trend lines appear once you have at least 3 saved predictions.")

    st.markdown("### Prediction history")
    table = df[["id", "created_at", *LABELS, "predicted_score", "category"]].rename(
        columns={"id": "ID", "created_at": "Date", "predicted_score": "Predicted", "category": "Category", **LABELS})
    st.dataframe(table, use_container_width=True, hide_index=True,
                 column_config={"Date": st.column_config.DatetimeColumn(format="DD MMM YYYY, HH:mm")})

    st.markdown("### Compare predictions")
    options = {_fmt(r): r["id"] for _, r in df.iterrows()}
    chosen = st.multiselect("Pick 2-4 predictions to compare", list(options), max_selections=4, key="cmp_sel")
    if len(chosen) >= 2:
        rows = df[df["id"].isin([options[c] for c in chosen])].sort_values("id")
        st.plotly_chart(charts.compare(rows), use_container_width=True, config={"displayModeBar": False})
        first, last = rows.iloc[0], rows.iloc[-1]
        diff = last["predicted_score"] - first["predicted_score"]
        st.info(f"Predicted score changed by **{diff:+.1f}** between #{int(first['id'])} and #{int(last['id'])}.")
    else:
        st.caption("Select at least two predictions to see a side-by-side comparison.")

    st.markdown("### Delete records")
    d1, d2 = st.columns(2, gap="large")
    with d1:
        to_del = st.multiselect("Select records to delete", list(options), key="del_sel")
        if st.button("Delete selected", disabled=not to_del, key="del_btn"):
            for label in to_del:
                database.delete_prediction(options[label])
            st.session_state.pop("del_sel", None)
            st.session_state.pop("cmp_sel", None)
            st.rerun()
    with d2:
        confirm = st.checkbox("I want to delete all my saved predictions", key="del_all_confirm")
        if st.button("Delete all history", disabled=not confirm, key="del_all_btn"):
            database.delete_all()
            for k in ("del_sel", "cmp_sel", "del_all_confirm"):
                st.session_state.pop(k, None)
            st.rerun()


def page_about() -> None:
    st.markdown("## About EduPredict AI")
    html("""
    <div class="flow">
    <div class="step">Student Data<small>5 inputs</small></div><div class="arrow">→</div>
    <div class="step">Data Preprocessing<small>validate &amp; clean</small></div><div class="arrow">→</div>
    <div class="step">ML Model<small>Random Forest</small></div><div class="arrow">→</div>
    <div class="step">Score Prediction<small>0-100</small></div><div class="arrow">→</div>
    <div class="step">Performance Insights<small>category &amp; tips</small></div>
    </div>
    """)
    st.write("")
    blocks = [
        ("What is EduPredict AI?", "A student-friendly tool that estimates an exam score from five everyday habits: study hours, "
         "attendance, previous marks, assignment completion and sleep. It is a learning project, not an official assessment."),
        ("How does machine learning work?", "Instead of following hand-written rules, a model studies many past examples (inputs and the "
         "score that followed) and learns patterns. It is then tested on examples it has never seen to check it generalises."),
        ("What is Random Forest Regression?", "A Random Forest builds many decision trees, each trained on a random sample of the data, "
         "and averages their predictions. Averaging makes it more stable than a single tree and lets it capture non-linear effects, "
         "such as study time having diminishing returns."),
        ("What data is used?", "The five inputs listed above, and a final score as the target. The bundled dataset is "
         "<b>synthetic</b> (2,000 generated rows from a hand-written formula plus random noise) - it contains no real students."),
        ("How are predictions generated?", "Your inputs are validated, arranged in the same column order as training, and passed to the "
         "saved model (<code>models/model.pkl</code>). The output is clipped to 0-100. Nothing is hard-coded."),
        ("Limitations", "The demo model learned from synthetic data, so its relationships are assumptions, not real-world findings. "
         "It ignores subject difficulty, teaching quality, health, motivation and many other factors, and is less reliable outside "
         "the input ranges it saw. <b>Predictions are estimates, not guaranteed academic outcomes.</b>"),
    ]
    for i in range(0, len(blocks), 2):
        cols = st.columns(2, gap="medium")
        for col, (t, d) in zip(cols, blocks[i:i + 2]):
            col.markdown(f'<div class="card"><h4 style="color:#F0D77A">{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
        st.write("")

    st.markdown("### Model evaluation")
    if BUNDLE is None:
        st.warning("Train the model (`python -m src.train`) to see evaluation metrics.")
        return
    m = BUNDLE["metrics"]
    table = pd.DataFrame([{"Model": k, "MAE (lower is better)": round(v["mae"], 2), "R² (higher is better)": round(v["r2"], 3)}
                          for k, v in m.items()])
    e1, e2 = st.columns([1, 1.2], gap="large")
    with e1:
        st.dataframe(table, hide_index=True, use_container_width=True)
        st.caption(f"Trained on {BUNDLE['n_train']} rows and scored on {BUNDLE['n_test']} separate held-out rows "
                   f"({BUNDLE['trained_at'][:10]}). Linear Regression is included for comparison; Random Forest is the model used. "
                   "These scores describe fit to the synthetic dataset, not real-world accuracy.")
    with e2:
        st.plotly_chart(charts.importances(BUNDLE["feature_importances"]), use_container_width=True,
                        config={"displayModeBar": False})


{"Home": page_home, "Predict Performance": page_predict, "Analytics": page_analytics,
 "About Project": page_about}[st.session_state["page"]]()
