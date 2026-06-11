import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API_BASE = "http://web-api:4000"

st.title("Priority Countries")
st.write(
    "Countries flagged for immediate humanitarian attention based on climate pressure, "
    "asylum volume, and economic vulnerability."
)
st.divider()

# fetch risk data
try:
    r = requests.get(f"{API_BASE}/risk-classifications", timeout=5)
    risks = r.json() if r.status_code == 200 else []
except Exception:
    risks = []

if not risks:
    st.warning("No data available. Make sure the backend is running.")
    st.stop()

# keep only the most recent year per country, sorted by score
seen = {}
for row in risks:
    cid = row["country_id"]
    if cid not in seen or row["year"] > seen[cid]["year"]:
        seen[cid] = row
rows = sorted(seen.values(), key=lambda x: float(x.get("risk_score") or 0), reverse=True)

# notes field looks like "climate=61.5, asylum=96.2, vulnerability=15.4"
# split it into a dict of {key: float}
def parse_notes(notes):
    comp = {}
    for part in (notes or "").split(","):
        if "=" in part:
            k, v = part.strip().split("=")
            comp[k.strip()] = float(v.strip())
    return comp

# return whichever component (climate / asylum / vulnerability) scored highest
DRIVER_LABELS = {
    "climate":       "🌡️ Climate Pressure",
    "asylum":        "🧳 Asylum Volume",
    "vulnerability": "📉 Economic Vulnerability",
}

def top_driver(comp):
    if not comp:
        return "—"
    return DRIVER_LABELS.get(max(comp, key=comp.get), "—")

# draw a simple colored progress bar in HTML
def score_bar(value, color):
    pct = min(int(value), 100)
    return (
        f"<div style='background:#e0e0e0;border-radius:4px;height:10px;width:100%;margin-top:3px'>"
        f"<div style='background:{color};width:{pct}%;height:10px;border-radius:4px'></div>"
        f"</div>"
    )

COLORS = {"climate": "#e05c2a", "asylum": "#3a7abf", "vulnerability": "#8b5cf6"}

critical = [r for r in rows if r.get("risk_level") == "Critical"]
high     = [r for r in rows if r.get("risk_level") == "High"]

# ── Critical cards ────────────────────────────────────────────────────────────
if critical:
    st.subheader("🔴 Critical — Immediate Attention Needed")
    st.caption(f"{len(critical)} {'country' if len(critical) == 1 else 'countries'} at critical risk")
    st.write("")

    cols = st.columns(min(len(critical), 4))

    for i, row in enumerate(critical):
        comp  = parse_notes(row.get("notes"))
        score = float(row.get("risk_score") or 0)

        with cols[i % len(cols)]:
            st.markdown(
                f"""
                <div style='border:2px solid #e05c2a;border-radius:10px;padding:18px 16px;background:#fff8f5'>
                    <div style='font-size:1.25rem;font-weight:700'>{row['country_name']}</div>
                    <div style='font-size:2rem;font-weight:800;color:#e05c2a'>{score:.1f}<span style='font-size:1rem;color:#888'>/100</span></div>
                    <div style='font-size:0.8rem;color:#555;margin-bottom:10px'>Main driver: <strong>{top_driver(comp)}</strong></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")

            for key, label in [("climate", "Climate"), ("asylum", "Asylum"), ("vulnerability", "Vulnerability")]:
                if key in comp:
                    st.markdown(
                        f"<span style='font-size:0.75rem;color:#444'>{label}: <strong>{comp[key]:.0f}</strong></span>"
                        + score_bar(comp[key], COLORS[key]),
                        unsafe_allow_html=True,
                    )
                    st.write("")

    st.divider()

# ── High rows ─────────────────────────────────────────────────────────────────
if high:
    st.subheader("🟠 High — Monitor Closely")
    st.caption(f"{len(high)} countries at high risk")
    st.write("")

    for row in high:
        comp  = parse_notes(row.get("notes"))
        score = float(row.get("risk_score") or 0)

        c1, c2, c3, c4 = st.columns([3, 1.5, 2, 3])
        c1.markdown(f"**{row['country_name']}**")
        c2.markdown(f"<span style='font-size:1.1rem;font-weight:700;color:#d97706'>{score:.1f}</span>", unsafe_allow_html=True)
        c3.markdown(f"<span style='font-size:0.8rem;color:#555'>{top_driver(comp)}</span>", unsafe_allow_html=True)

        bar_html = ""
        for key, color in COLORS.items():
            if key in comp:
                bar_html += (
                    f"<div style='display:inline-block;width:30%;margin-right:2%'>"
                    f"<div style='font-size:0.65rem;color:#777'>{key.title()[:4]} {comp[key]:.0f}</div>"
                    + score_bar(comp[key], color) +
                    f"</div>"
                )
        c4.markdown(f"<div style='padding-top:4px'>{bar_html}</div>", unsafe_allow_html=True)

        st.divider()
