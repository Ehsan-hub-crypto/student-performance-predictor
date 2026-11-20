"""Plotly charts in the gold / white / black theme."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.preprocess import LABELS, LIMITS

GOLD, GOLD_2, WHITE, GREY, DARK_GREY = "#D4AF37", "#F0D77A", "#FFFFFF", "#B8B8B8", "#8A8A8A"
CARD, GRID = "#171717", "#303030"
CATEGORY_COLORS = {"Excellent": GOLD, "Good": GOLD_2, "Average": WHITE, "Needs Improvement": DARK_GREY}


def _style(fig: go.Figure, height: int = 340) -> go.Figure:
    fig.update_layout(
        height=height, paper_bgcolor=CARD, plot_bgcolor=CARD, font=dict(color=WHITE, family="Inter, sans-serif"),
        margin=dict(l=16, r=16, t=48, b=16), title=dict(font=dict(size=15)), legend=dict(font=dict(color=GREY)),
    )
    fig.update_xaxes(gridcolor=GRID, zerolinecolor=GRID, color=GREY)
    fig.update_yaxes(gridcolor=GRID, zerolinecolor=GRID, color=GREY)
    return fig


def gauge(score: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge", value=score,
        gauge=dict(axis=dict(range=[0, 100], tickcolor=GREY), bar=dict(color=GOLD, thickness=0.3),
                   bgcolor="#222", borderwidth=0),
    ))
    return _style(fig, 200).update_layout(margin=dict(l=36, r=36, t=24, b=0))


def breakdown(inputs: dict) -> go.Figure:
    """Each input shown as a % of its maximum so different units can be compared."""
    names = list(LABELS)
    pct = [inputs[n] / LIMITS[n][1] * 100 for n in names]
    text = [f"{inputs[n]:g}" + ("h" if "hours" in n else "%" if n in ("attendance", "assignment_completion") else "")
            for n in names]
    fig = go.Figure(go.Bar(
        x=pct, y=[LABELS[n] for n in names], orientation="h", text=text, textposition="outside",
        marker=dict(color=GOLD), cliponaxis=False, hovertemplate="%{y}: %{text}<extra></extra>",
    ))
    fig.update_xaxes(range=[0, 118], title="Share of maximum value (%)")
    fig.update_yaxes(autorange="reversed")
    return _style(fig, 330).update_layout(title="Your inputs at a glance")


def radar(inputs: dict) -> go.Figure:
    names = list(LABELS)
    pct = [inputs[n] / LIMITS[n][1] * 100 for n in names]
    labels = [LABELS[n] for n in names]
    fig = go.Figure(go.Scatterpolar(r=pct + pct[:1], theta=labels + labels[:1], fill="toself",
                                    line=dict(color=GOLD), fillcolor="rgba(212,175,55,.25)"))
    fig.update_layout(polar=dict(bgcolor=CARD, radialaxis=dict(range=[0, 100], gridcolor=GRID, color=GREY),
                                 angularaxis=dict(gridcolor=GRID, color=WHITE)), showlegend=False)
    return _style(fig, 330).update_layout(title="Profile shape")


def category_distribution(df: pd.DataFrame, order: list[str]) -> go.Figure:
    counts = df["category"].value_counts().reindex(order, fill_value=0)
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values, marker=dict(color=[CATEGORY_COLORS[c] for c in counts.index]),
                           text=counts.values, textposition="outside"))
    fig.update_yaxes(dtick=1, title="Predictions")
    return _style(fig).update_layout(title="Performance category distribution")


def scatter(df: pd.DataFrame, x: str, title: str, xlabel: str) -> go.Figure:
    fig = go.Figure(go.Scatter(x=df[x], y=df["predicted_score"], mode="markers",
                               marker=dict(color=GOLD, size=10, line=dict(color=WHITE, width=1)),
                               hovertemplate=xlabel + ": %{x}<br>Predicted: %{y}<extra></extra>"))
    if len(df) >= 3 and df[x].nunique() > 1:  # trend line only when it means something
        k, b = np.polyfit(df[x], df["predicted_score"], 1)
        xs = np.array([df[x].min(), df[x].max()])
        fig.add_trace(go.Scatter(x=xs, y=k * xs + b, mode="lines", line=dict(color=WHITE, dash="dash", width=1.5),
                                 name="Trend", hoverinfo="skip"))
    fig.update_xaxes(title=xlabel)
    fig.update_yaxes(title="Predicted score", range=[0, 100])
    return _style(fig).update_layout(title=title, showlegend=False)


def history_line(df: pd.DataFrame) -> go.Figure:
    d = df.sort_values("created_at")
    fig = go.Figure(go.Scatter(x=d["created_at"], y=d["predicted_score"], mode="lines+markers",
                               line=dict(color=GOLD), marker=dict(color=GOLD_2, size=8)))
    fig.update_yaxes(range=[0, 100], title="Predicted score")
    return _style(fig).update_layout(title="Predicted score over time")


def compare(rows: pd.DataFrame) -> go.Figure:
    """Grouped bars comparing selected predictions across the five inputs (as % of max)."""
    palette = [GOLD, WHITE, GOLD_2, DARK_GREY, "#8C7320"]
    fig = go.Figure()
    for i, (_, r) in enumerate(rows.iterrows()):
        fig.add_trace(go.Bar(
            name=f"#{int(r['id'])} - {r['predicted_score']:.1f}",
            x=[LABELS[n] for n in LABELS], y=[r[n] / LIMITS[n][1] * 100 for n in LABELS],
            marker=dict(color=palette[i % len(palette)]),
        ))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Share of maximum (%)", range=[0, 100])
    return _style(fig, 360).update_layout(title="Input comparison")


def importances(imp: dict) -> go.Figure:
    items = sorted(imp.items(), key=lambda kv: kv[1])
    fig = go.Figure(go.Bar(x=[v * 100 for _, v in items], y=[LABELS[k] for k, _ in items], orientation="h",
                           marker=dict(color=GOLD), text=[f"{v * 100:.1f}%" for _, v in items], textposition="outside",
                           cliponaxis=False))
    fig.update_xaxes(title="Relative importance (%)", range=[0, max(v for v in imp.values()) * 100 * 1.2])
    return _style(fig, 300).update_layout(title="What the model relies on most")
