import streamlit as st

st.set_page_config(
    page_title="POG RTIP | Real-Time Intelligence Platform",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ---- sidebar ---- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0f1e 0%, #0d1b3e 60%, #0a2240 100%);
    border-right: 1px solid rgba(255,165,0,0.15);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Hide the auto-generated page list Streamlit adds for multi-page apps */
[data-testid="stSidebarNav"] { display: none !important; }

/* ---- nav buttons ---- */
div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    border-radius: 8px;
    color: #94a3b8 !important;
    font-size: 0.9rem;
    padding: 10px 14px;
    margin: 2px 0;
    cursor: pointer;
    transition: all 0.2s;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(249,115,22,0.12) !important;
    color: #f97316 !important;
}
div[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none !important;
}

/* ---- metric cards ---- */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid rgba(255,165,0,0.2);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}
[data-testid="metric-container"] label {
    color: #94a3b8 !important; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f8fafc !important; font-size: 1.8rem; font-weight: 700;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.8rem; }

/* ---- main area ---- */
.main .block-container { background: #060d1f; padding-top: 1.5rem; }
body, .stApp { background-color: #060d1f; }

/* ---- section headers ---- */
.section-header {
    color: #f8fafc; font-size: 1.05rem; font-weight: 600; letter-spacing: 0.5px;
    border-left: 3px solid #f97316; padding-left: 10px; margin: 1.5rem 0 0.75rem 0;
}
.page-title  { font-size: 1.6rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.2rem; }
.page-subtitle { font-size: 0.85rem; color: #64748b; margin-bottom: 1.5rem; }

hr { border-color: rgba(255,165,0,0.1) !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Page state ───────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "executive"

PAGES = [
    ("executive",  "🏠",  "Executive Command Center"),
    ("revenue",    "💰",  "Revenue & Sales Analytics"),
    ("inventory",  "🛢️",  "Inventory & Tank Monitoring"),
    ("fraud",      "🚨",  "Fraud & Loss Monitoring"),
    ("pump",       "🔧",  "Pump Health & Maintenance"),
    ("station360", "📡",  "Station 360 & Network Map"),
]

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 0 1rem 0;">
        <div style="font-size:2.8rem;">⛽</div>
        <div style="font-size:1.1rem;font-weight:700;color:#f97316;letter-spacing:1px;">POG RTIP</div>
        <div style="font-size:0.65rem;color:#64748b;letter-spacing:2.5px;margin-top:3px;">REAL-TIME INTELLIGENCE PLATFORM</div>
    </div>
    <hr style="border-color:rgba(249,115,22,0.3);margin:0 0 0.5rem 0;">
    """, unsafe_allow_html=True)

    for key, icon, label in PAGES:
        active = st.session_state.page == key
        btn_style = (
            "background:rgba(249,115,22,0.15) !important;"
            "color:#f97316 !important;"
            "border-left:3px solid #f97316 !important;"
            "border-radius:8px;"
        ) if active else ""
        if st.button(f"{icon}  {label}", key=f"nav_{key}",
                    use_container_width=True,
                    help=label):

            st.session_state.page = key

        if active:
            # inject active style via JS trick using a hidden marker
            st.markdown(
                f"""<style>
                div[data-testid="stSidebar"] button[kind="secondary"]:has(+ *) {{}}
                </style>""",
                unsafe_allow_html=True,
            )

    st.markdown("""
    <hr style="border-color:rgba(249,115,22,0.1);margin:1rem 0 0.5rem 0;">
    <div style="font-size:0.68rem;color:#475569;text-align:center;padding-bottom:0.5rem;">
        Source: Databricks Gold Layer<br>
        Cache TTL: 60 seconds
    </div>
    """, unsafe_allow_html=True)

# ── Route ────────────────────────────────────────────────────────────────────
p = st.session_state.page
if p == "executive":
    from pages import p1_executive;   p1_executive.render()
elif p == "revenue":
    from pages import p2_revenue;     p2_revenue.render()
elif p == "inventory":
    from pages import p3_inventory;   p3_inventory.render()
elif p == "fraud":
    from pages import p4_fraud;       p4_fraud.render()
elif p == "pump":
    from pages import p5_pump;        p5_pump.render()
elif p == "station360":
    from pages import p6_station360;  p6_station360.render()
