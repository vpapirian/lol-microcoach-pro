from __future__ import annotations

import os
import time
from dataclasses import asdict
from typing import Dict, Any, Optional, List

import pandas as pd
import plotly.express as px
import streamlit as st

from microcoach.config import Config
from microcoach.baselines import load_baselines
from microcoach.live_client import is_available as live_available, get_all
from microcoach.metrics import compute_snapshot, Snapshot
from microcoach.compare import compare_to_baseline

CFG = Config()

st.set_page_config(
    page_title="MicroCoach Pro",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Styling (insane but clean) ----
CUSTOM_CSS = """
<style>
:root {
  --bg: #0b0f17;
  --card: rgba(255,255,255,0.06);
  --card2: rgba(255,255,255,0.09);
  --stroke: rgba(255,255,255,0.10);
  --text: rgba(255,255,255,0.92);
  --muted: rgba(255,255,255,0.68);
  --accent: rgba(148, 163, 255, 1);
  --accent2: rgba(110, 231, 183, 1);
}
.stApp {
  background: radial-gradient(1200px 600px at 20% 10%, rgba(148,163,255,0.20), transparent 60%),
              radial-gradient(1200px 700px at 80% 0%, rgba(110,231,183,0.16), transparent 55%),
              radial-gradient(900px 600px at 60% 90%, rgba(236, 72, 153, 0.12), transparent 55%),
              var(--bg);
  color: var(--text);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
  border-right: 1px solid var(--stroke);
}
.block-container { padding-top: 1.2rem; }
h1,h2,h3 { letter-spacing: -0.02em; }
.mc-card {
  background: linear-gradient(180deg, var(--card), rgba(255,255,255,0.03));
  border: 1px solid var(--stroke);
  border-radius: 18px;
  padding: 16px 16px;
  box-shadow: 0 10px 35px rgba(0,0,0,0.28);
}
.mc-hero {
  border-radius: 22px;
  padding: 18px 18px;
  border: 1px solid rgba(255,255,255,0.10);
  background:
    radial-gradient(900px 300px at 20% 0%, rgba(148,163,255,0.24), transparent 60%),
    radial-gradient(700px 300px at 80% 0%, rgba(110,231,183,0.18), transparent 55%),
    linear-gradient(180deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
  box-shadow: 0 10px 40px rgba(0,0,0,0.34);
}
.mc-pill {
  display:inline-flex; align-items:center; gap:8px;
  padding: 6px 10px; border-radius: 999px;
  border: 1px solid var(--stroke);
  background: rgba(255,255,255,0.05);
  color: var(--muted); font-size: 0.90rem;
}
.mc-badge {
  padding: 2px 10px;
  border-radius: 999px;
  background: rgba(148,163,255,0.18);
  border: 1px solid rgba(148,163,255,0.30);
  color: var(--text);
  font-weight: 600;
}
div[data-testid="stMetricValue"] { font-size: 1.35rem; }
.small-muted { color: var(--muted); font-size: 0.92rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---- Sidebar ----
st.sidebar.markdown("## 🎮 MicroCoach Pro")
st.sidebar.caption("Responsive live dashboard for League of Legends (read-only).")

tier = st.sidebar.selectbox("Baseline Tier", ["Bronze","Silver","Gold","Platinum","Diamond"], index=2)
refresh = st.sidebar.slider("Refresh (seconds)", 0.25, 3.0, float(CFG.refresh_seconds), 0.25)
st.sidebar.divider()

auto_refresh = st.sidebar.toggle("Auto-refresh", value=True)
show_debug = st.sidebar.toggle("Show debug panel", value=False)

st.sidebar.markdown("### Connections")
raw = get_all(timeout=1.0)
st.subheader("LIVE CLIENT RAW RESPONSE")
st.json(raw)

live_ok = raw is not None


st.sidebar.write("Live Client API:", "✅ Online" if live_ok else "❌ Offline")
st.sidebar.caption("Live Client Data API is only online while you're in a game and API is enabled.")

# ---- Load baselines (cached) ----
@st.cache_data(show_spinner=False)
def _get_baselines(path: str):
    return load_baselines(path)

baselines = _get_baselines(CFG.baselines_path)

# ---- Session state for time series ----
if "history" not in st.session_state:
    st.session_state.history = []  # list[dict]

def push_history(snap: Snapshot):
    row = asdict(snap)
    st.session_state.history.append(row)
    # keep last ~10 minutes at 1s refresh -> 600 points
    if len(st.session_state.history) > 800:
        st.session_state.history = st.session_state.history[-800:]

def header():
    st.markdown(
        """<div class="mc-hero">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:12px; flex-wrap:wrap;">
          <div>
            <div class="mc-pill">⚡ Live, responsive • 🧠 Baseline comparisons • 📈 Time-series</div>
            <h1 style="margin:8px 0 2px 0;">MicroCoach Pro</h1>
            <div class="small-muted">Connects to your local League client APIs and turns it into a coaching dashboard.</div>
          </div>
          <div style="display:flex; gap:10px; align-items:center;">
            <span class="mc-badge">Tier: %s</span>
            <span class="mc-pill">Refresh: %ss</span>
          </div>
        </div>
        </div>""" % (tier, refresh),
        unsafe_allow_html=True
    )

def get_snapshot() -> Optional[Snapshot]:
    if raw is None:
        return None
    return compute_snapshot(raw)


def kpi_row(snap: Snapshot):
    c1, c2, c3, c4, c5 = st.columns(5)
    mins = snap.game_time / 60.0
    c1.metric("Champion", snap.champion_name)
    c2.metric("Level", snap.level)
    c3.metric("K / D / A", f"{snap.kills}/{snap.deaths}/{snap.assists}")
    c4.metric("CS", snap.cs)
    c5.metric("CS / min", f"{snap.cs_per_min:.2f}")

    st.caption(f"Game time: {mins:,.1f} min • Gold: {snap.current_gold:,}")

def score_cards(snap: Snapshot):
    mv_base = baselines["movement_score"][tier]
    cs_base = baselines["cs_per_min"][tier]

    mv_cmp = compare_to_baseline(snap.movement_score, mv_base.mean, mv_base.std, tier=tier)
    cs_cmp = compare_to_baseline(snap.cs_per_min, cs_base.mean, cs_base.std, tier=tier)

    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="mc-card">', unsafe_allow_html=True)
        st.subheader("🕹️ Movement / Micro Score")
        st.metric("Score", f"{snap.movement_score:.1f}", help="Demo metric. Replace with your real micro features.")
        if mv_cmp.z is not None:
            st.write(f"Z-score vs {tier}: **{mv_cmp.z:+.2f}** • Percentile: **{mv_cmp.percentile_approx:.0f}th**")
        st.caption(f"Baseline ({tier}): mean {mv_base.mean:.1f} • std {mv_base.std:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="mc-card">', unsafe_allow_html=True)
        st.subheader("📌 CS / min")
        st.metric("CS/min", f"{snap.cs_per_min:.2f}")
        if cs_cmp.z is not None:
            st.write(f"Z-score vs {tier}: **{cs_cmp.z:+.2f}** • Percentile: **{cs_cmp.percentile_approx:.0f}th**")
        st.caption(f"Baseline ({tier}): mean {cs_base.mean:.1f} • std {cs_base.std:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)

def charts():
    if not st.session_state.history:
        st.info("No history yet — start a game and enable Auto-refresh.")
        return
    df = pd.DataFrame(st.session_state.history)
    df["t_min"] = df["game_time"] / 60.0

    c1, c2 = st.columns([1,1])
    with c1:
        fig = px.line(df, x="t_min", y="movement_score", title="Movement/Micro Score (over time)")
        fig.update_layout(margin=dict(l=10,r=10,t=45,b=10), height=330)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(df, x="t_min", y="cs_per_min", title="CS per minute (over time)")
        fig.update_layout(margin=dict(l=10,r=10,t=45,b=10), height=330)
        st.plotly_chart(fig, use_container_width=True)

def debug_panel(raw: Dict[str, Any]):
    with st.expander("Debug: raw /allgamedata", expanded=False):
        st.json(raw)

# ---- Main UI ----
header()

tab1, tab2, tab3 = st.tabs(["Dashboard", "Insights", "Settings"])

with tab1:
    st.markdown('<div class="mc-card">', unsafe_allow_html=True)

    snap = get_snapshot()

    if not snap:
        st.warning("Live Client API is offline. Start a game and enable the Live Client Data API in settings.")
    else:
        push_history(snap)
        kpi_row(snap)

    st.markdown("</div>", unsafe_allow_html=True)

    if snap:
        score_cards(snap)
        charts()

with tab2:
    st.markdown('<div class="mc-card">', unsafe_allow_html=True)
    st.subheader("🧠 Coaching Insights (starter)")
    st.write(
        "This section is where your real micro features go (mouse path efficiency, click cadence, camera control, spacing, etc.). "
        "Right now it provides safe, baseline-driven prompts based on the demo metrics."
    )

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        last = df.iloc[-1]
        tips: List[str] = []
        if float(last["cs_per_min"]) < baselines["cs_per_min"][tier].mean - baselines["cs_per_min"][tier].std:
            tips.append("Your CS/min is below baseline. Prioritize wave timing: prep last-hits before trades.")
        if float(last["movement_score"]) < baselines["movement_score"][tier].mean - baselines["movement_score"][tier].std:
            tips.append("Micro score is below baseline. Focus on minimizing dead time: move with purpose between last-hits.")
        if not tips:
            tips.append("You’re tracking at or above baseline. Push advantage: trade on enemy last-hit windows.")

        for t in tips:
            st.markdown(f"- {t}")
    else:
        st.info("Start a game to generate insights.")

    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="mc-card">', unsafe_allow_html=True)
    st.subheader("⚙️ Connections & Settings")
    st.write("**Live Client Data API** must be enabled in the LoL client settings and is only online while in-game.")
    st.code("http://127.0.0.1:2999/liveclientdata/allgamedata", language="text")

    st.write("Baselines file:")
    st.code(CFG.baselines_path, language="text")
    st.caption("Edit `data/baselines.json` to tune tiers to your own data.")
    st.markdown("</div>", unsafe_allow_html=True)

if auto_refresh and live_ok:
    time.sleep(refresh)
    try:
        st.rerun()  # newer streamlit
    except Exception:
        st.experimental_rerun()  # older streamlit
