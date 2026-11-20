"""Global CSS (black / gold / white theme) and small HTML helpers."""
import streamlit as st

GOLD, GOLD_2 = "#D4AF37", "#F0D77A"
BG, BG_2, CARD = "#080808", "#111111", "#171717"
TEXT, MUTED, BORDER = "#FFFFFF", "#B8B8B8", "#303030"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
:root {{ --gold:{GOLD}; --gold2:{GOLD_2}; --bg:{BG}; --bg2:{BG_2}; --card:{CARD}; --text:{TEXT}; --muted:{MUTED}; --border:{BORDER}; }}
html, body, [class*="css"], .stApp {{ font-family:'Inter',sans-serif; color:var(--text); }}
.stApp {{ background: radial-gradient(1200px 500px at 85% -10%, rgba(212,175,55,.10), transparent 60%), var(--bg); }}
header[data-testid="stHeader"] {{ background:transparent; }}
#MainMenu, footer, .stAppDeployButton {{ visibility:hidden; }}
.block-container {{ max-width:1180px; padding-top:4.2rem; padding-bottom:4rem; }}
h1,h2,h3 {{ font-family:'Playfair Display',serif; letter-spacing:-.01em; color:var(--text); }}
p, li, label, span {{ color:inherit; }}
a {{ color:var(--gold); }}
[data-testid="stSidebar"] {{ background:var(--bg2); border-right:1px solid var(--border); }}

/* ---- navigation ---- */
.brand {{ display:flex; align-items:center; gap:.6rem; font-family:'Playfair Display',serif; font-weight:700; font-size:1.35rem; white-space:nowrap; }}
.brand .dot {{ width:30px; height:30px; border-radius:9px; background:linear-gradient(135deg,{GOLD},{GOLD_2}); display:grid; place-items:center; color:#080808; font-size:1rem; font-weight:700; }}
.brand b {{ color:var(--gold); }}
[data-testid="stRadio"] > div[role="radiogroup"] {{ gap:.25rem; flex-wrap:wrap; justify-content:center; }}
label[data-testid="stRadioOption"] {{ background:transparent; border:1px solid transparent; border-radius:999px; padding:.35rem .95rem; cursor:pointer; transition:all .2s; }}
label[data-testid="stRadioOption"]:hover {{ border-color:var(--border); }}
label[data-testid="stRadioOption"] > div > div:first-child {{ display:none; }}
label[data-testid="stRadioOption"] p {{ color:var(--muted); font-weight:500; font-size:.92rem; }}
label[data-testid="stRadioOption"][data-selected="true"] {{ background:rgba(212,175,55,.12); border-color:rgba(212,175,55,.45); }}
label[data-testid="stRadioOption"][data-selected="true"] p {{ color:var(--gold2); }}
.gh {{ display:inline-grid; place-items:center; width:38px; height:38px; border:1px solid var(--border); border-radius:10px; transition:all .2s; }}
.gh:hover {{ border-color:var(--gold); }}
.gh svg {{ fill:var(--text); width:19px; height:19px; }}
hr.nav {{ border:0; border-top:1px solid var(--border); margin:.6rem 0 1.4rem; }}

/* ---- buttons ---- */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {{ border-radius:10px; border:1px solid var(--border); background:var(--card); color:var(--text); font-weight:600; transition:all .2s; min-height:2.6rem; }}
.stButton > button:hover, .stFormSubmitButton > button:hover {{ border-color:var(--gold); color:var(--gold2); }}
.stButton > button[kind^="primary"], .stFormSubmitButton > button[kind^="primary"] {{ background:linear-gradient(135deg,{GOLD},{GOLD_2}); color:#080808; border:0; box-shadow:0 6px 22px rgba(212,175,55,.22); }}
.stButton > button[kind^="primary"]:hover, .stFormSubmitButton > button[kind^="primary"]:hover {{ color:#080808; filter:brightness(1.06); transform:translateY(-1px); }}

/* ---- cards ---- */
.card {{ background:var(--card); border:1px solid var(--border); border-radius:18px; padding:1.3rem 1.4rem; box-shadow:0 10px 30px rgba(0,0,0,.35); height:100%; }}
.card h4 {{ margin:0 0 .35rem; font-size:1.02rem; color:var(--text); }}
.card p {{ margin:0; color:var(--muted); font-size:.94rem; line-height:1.55; }}
.kpi {{ background:var(--card); border:1px solid var(--border); border-radius:16px; padding:1rem 1.2rem; }}
.kpi .l {{ color:var(--muted); font-size:.8rem; text-transform:uppercase; letter-spacing:.08em; }}
.kpi .v {{ font-family:'Playfair Display',serif; font-size:1.9rem; color:var(--gold2); }}
.eyebrow {{ color:var(--gold); font-size:.78rem; letter-spacing:.18em; text-transform:uppercase; font-weight:600; }}
.muted {{ color:var(--muted); }}
.pill {{ display:inline-block; border:1px solid rgba(212,175,55,.5); color:var(--gold2); border-radius:999px; padding:.2rem .8rem; font-size:.78rem; font-weight:600; }}
.pill.gen {{ border-color:var(--border); color:var(--muted); }}
.note {{ border-left:3px solid var(--gold); background:rgba(212,175,55,.06); padding:.7rem 1rem; border-radius:0 10px 10px 0; color:var(--muted); font-size:.9rem; }}

/* ---- hero ---- */
.hero .h1 {{ font-family:'Playfair Display',serif; font-weight:700;  font-size:clamp(2.2rem,5vw,3.7rem); line-height:1.08; margin:.5rem 0 1rem; }}
.hero .h1 span {{ background:linear-gradient(120deg,{GOLD},{GOLD_2}); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.hero p.sub {{ color:var(--muted); font-size:1.08rem; max-width:34rem; line-height:1.6; }}
.orb {{ position:relative; width:min(340px,80vw); aspect-ratio:1; margin:0 auto; }}
.orb .ring {{ position:absolute; inset:0; border-radius:50%; border:1px solid rgba(212,175,55,.35); animation:spin 28s linear infinite; }}
.orb .ring:nth-child(2) {{ inset:12%; border-style:dashed; animation-duration:40s; animation-direction:reverse; }}
.orb .ring:nth-child(3) {{ inset:26%; border-color:rgba(240,215,122,.5); animation-duration:22s; }}
.orb .ring::after {{ content:""; position:absolute; top:-5px; left:50%; width:10px; height:10px; border-radius:50%; background:var(--gold2); box-shadow:0 0 14px var(--gold); }}
.orb .core {{ position:absolute; inset:38%; border-radius:50%; background:radial-gradient(circle at 35% 30%, {GOLD_2}, {GOLD} 55%, #7a6317); display:grid; place-items:center; color:#080808; font-weight:700; font-family:'Playfair Display',serif; font-size:1.5rem; animation:pulse 4s ease-in-out infinite; box-shadow:0 0 60px rgba(212,175,55,.35); }}
@keyframes spin {{ to {{ transform:rotate(360deg); }} }}
@keyframes pulse {{ 50% {{ transform:scale(1.06); box-shadow:0 0 80px rgba(212,175,55,.5); }} }}
@media (prefers-reduced-motion: reduce) {{ .orb .ring, .orb .core {{ animation:none; }} }}

/* ---- score ---- */
.score-card {{ text-align:center; background:linear-gradient(160deg,#1d1a10,{CARD} 60%); border:1px solid rgba(212,175,55,.4); border-radius:20px; padding:1.6rem 1rem; }}
.score-card .num {{ font-family:'Playfair Display',serif; font-size:clamp(3.5rem,9vw,5.5rem); line-height:1; background:linear-gradient(120deg,{GOLD},{GOLD_2}); -webkit-background-clip:text; background-clip:text; color:transparent; }}
.score-card .of {{ color:var(--muted); font-size:1rem; }}
.flow {{ display:flex; flex-wrap:wrap; gap:.6rem; align-items:stretch; justify-content:center; }}
.flow .step {{ flex:1 1 150px; background:var(--card); border:1px solid var(--border); border-radius:14px; padding:.9rem; text-align:center; font-weight:600; font-size:.92rem; }}
.flow .step small {{ display:block; color:var(--muted); font-weight:400; margin-top:.25rem; }}
.flow .arrow {{ align-self:center; color:var(--gold); font-size:1.2rem; }}
@media (max-width:640px) {{ .flow .arrow {{ display:none; }} }}

/* ---- inputs ---- */
[data-testid="stSlider"] [role="slider"] {{ background:var(--gold); }}
.stNumberInput input {{ background:var(--bg2); border-color:var(--border); color:var(--text); }}
[data-testid="stForm"] {{ background:var(--card); border:1px solid var(--border); border-radius:18px; padding:1.4rem; }}
.hint {{ color:var(--muted); font-size:.85rem; margin:-.5rem 0 1rem; }}
[data-testid="stMetric"] {{ background:var(--card); border:1px solid var(--border); border-radius:14px; padding:.8rem 1rem; }}
[data-testid="stMetricValue"] {{ color:var(--gold2); }}
.stDataFrame {{ border:1px solid var(--border); border-radius:12px; }}
.stTabs [aria-selected="true"] {{ color:var(--gold2); }}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def html(markup: str) -> None:
    """Render HTML safely through Markdown: strip indentation and blank lines first."""
    cleaned = "\n".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)
