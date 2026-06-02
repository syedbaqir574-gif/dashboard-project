"""
app.py — Main Dashboard Application
S&P 500 Constituents · Exploratory Data Analysis
Course: Exploratory Data Analysis | Instructor: Ali Hassan Sherazi
Submission: 05-June-2026
"""

import streamlit as st
import pandas as pd
import numpy as np

from filters import load_data, apply_filters
import charts as ch

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="S&P 500 Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

    /* Root theme */
    :root {
        --bg: #0f1923;
        --card: #162433;
        --accent: #2ea8cc;
        --accent2: #f2b705;
        --text: #e8edf2;
        --muted: #7a99b0;
        --border: #243447;
    }

    html, body, [class*="css"] {
        background-color: var(--bg);
        color: var(--text);
        font-family: 'Rajdhani', sans-serif;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0d1620 !important;
        border-right: 1px solid var(--border);
    }
    section[data-testid="stSidebar"] * { color: var(--text) !important; }

    /* KPI cards */
    .kpi-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-top: 3px solid var(--accent);
        border-radius: 8px;
        padding: 18px 20px 14px;
        text-align: center;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'Rajdhani', sans-serif;
        font-size: 32px;
        font-weight: 700;
        color: var(--accent);
        line-height: 1;
    }
    .kpi-sub {
        font-size: 11px;
        color: var(--muted);
        margin-top: 4px;
    }

    /* Section headers */
    .section-header {
        font-family: 'Share Tech Mono', monospace;
        font-size: 11px;
        color: var(--accent);
        text-transform: uppercase;
        letter-spacing: 2px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 6px;
        margin: 22px 0 14px;
    }

    /* Chart containers */
    .chart-box {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 14px;
    }

    /* Dashboard title */
    .dash-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: 2px;
        line-height: 1.1;
    }
    .dash-title span { color: var(--accent); }
    .dash-subtitle {
        font-family: 'Share Tech Mono', monospace;
        font-size: 12px;
        color: var(--muted);
        letter-spacing: 1.5px;
        margin-top: 6px;
    }

    /* Streamlit overrides */
    .stButton>button {
        background: var(--accent) !important;
        color: #0f1923 !important;
        border: none !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-weight: 700 !important;
        letter-spacing: 1px;
        border-radius: 4px !important;
    }
    div[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 6px; }

    /* Hide Streamlit branding */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Data Load ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
   base = os.path.dirname(os.path.abspath(__file__))
path = os.path.join(base, "data", "constituents.txt")
return load_data(path)

df_raw = get_data()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR FILTERS
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🔍 Filters")
    st.markdown("---")

    # ── Reset button ──────────────────────────────────────────────────────────
    if st.button("↺  Reset All Filters"):
        st.session_state.clear()
        st.rerun()

    st.markdown("#### 🏢 Sector")
    all_sectors = sorted(df_raw["GICS Sector"].dropna().unique().tolist())
    selected_sectors = st.multiselect(
        "Select Sectors", options=all_sectors,
        default=[], key="sectors",
        help="Leave empty to include all sectors"
    )

    st.markdown("#### 🏭 Sub-Industry")
    # Limit sub-industries to selected sectors when chosen
    if selected_sectors:
        sub_pool = df_raw[df_raw["GICS Sector"].isin(selected_sectors)]["GICS Sub-Industry"]
    else:
        sub_pool = df_raw["GICS Sub-Industry"]
    all_subs = sorted(sub_pool.dropna().unique().tolist())
    selected_subs = st.multiselect(
        "Select Sub-Industries", options=all_subs,
        default=[], key="subs"
    )

    st.markdown("#### 📍 HQ State / Country")
    all_states = sorted(df_raw["HQ_State"].dropna().unique().tolist())
    selected_states = st.multiselect(
        "Select HQ Location", options=all_states,
        default=[], key="states"
    )

    st.markdown("#### 📅 Year Added to S&P 500")
    min_ya = int(df_raw["Year_Added"].min())
    max_ya = int(df_raw["Year_Added"].max())
    year_added_range = st.slider(
        "Year Added Range", min_value=min_ya, max_value=max_ya,
        value=(min_ya, max_ya), key="year_added"
    )

    st.markdown("#### 🏗️ Year Founded")
    min_fy = int(df_raw["Founded_Year"].dropna().min())
    max_fy = int(df_raw["Founded_Year"].dropna().max())
    founded_range = st.slider(
        "Founded Year Range", min_value=min_fy, max_value=max_fy,
        value=(min_fy, max_fy), key="founded"
    )

    st.markdown("#### 📏 Company Age (Years)")
    min_age = int(df_raw["Company_Age"].dropna().min())
    max_age = int(df_raw["Company_Age"].dropna().max())
    age_range = st.slider(
        "Age Range", min_value=min_age, max_value=max_age,
        value=(min_age, max_age), key="age"
    )

    st.markdown("#### 🔎 Search")
    search_text = st.text_input(
        "Search by Symbol, Company, State, or Sub-Industry",
        value="", key="search",
        placeholder="e.g. Apple, Tech, California..."
    )


# ── Apply all filters (linked to every chart) ─────────────────────────────────
df = apply_filters(
    df_raw,
    sectors=selected_sectors or None,
    sub_industries=selected_subs or None,
    year_added_range=year_added_range,
    founded_range=founded_range,
    age_range=age_range,
    search_text=search_text,
    states=selected_states or None,
)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

# ── Dashboard Header ──────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 20px 0 10px;">
    <div class="dash-title">S&amp;P 500 <span>Constituents</span> Dashboard</div>
    <div class="dash-subtitle">// EXPLORATORY DATA ANALYSIS · S&amp;P 500 INDEX COMPANIES · GICS CLASSIFICATION</div>
</div>
""", unsafe_allow_html=True)

st.markdown("Analyze all **S&P 500** companies by sector, founding year, geography, and index tenure. Use the sidebar filters to drill into any segment — all charts update simultaneously.")

st.markdown("---")


# ── KPI Summary Cards ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">// KEY METRICS</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Companies</div>
        <div class="kpi-value">{len(df):,}</div>
        <div class="kpi-sub">of {len(df_raw)} total</div>
    </div>""", unsafe_allow_html=True)

with k2:
    avg_age = df["Company_Age"].dropna().mean()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg Company Age</div>
        <div class="kpi-value">{avg_age:.0f}</div>
        <div class="kpi-sub">years since founding</div>
    </div>""", unsafe_allow_html=True)

with k3:
    oldest = df.loc[df["Company_Age"].idxmax()] if len(df) > 0 else None
    oldest_name = oldest["Security"][:18] if oldest is not None else "—"
    oldest_age = int(oldest["Company_Age"]) if oldest is not None else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Oldest Company</div>
        <div class="kpi-value" style="font-size:22px">{oldest_name}</div>
        <div class="kpi-sub">{oldest_age} years old</div>
    </div>""", unsafe_allow_html=True)

with k4:
    sectors_count = df["GICS Sector"].nunique()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Sectors</div>
        <div class="kpi-value">{sectors_count}</div>
        <div class="kpi-sub">GICS sectors</div>
    </div>""", unsafe_allow_html=True)

with k5:
    avg_tenure = df["Years_in_SP500"].dropna().mean()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg S&P Tenure</div>
        <div class="kpi-value">{avg_tenure:.0f}</div>
        <div class="kpi-sub">years in index</div>
    </div>""", unsafe_allow_html=True)

st.markdown("")


# ── SECTION 1: Sector Overview ───────────────────────────────────────────────
st.markdown('<div class="section-header">// SECTOR OVERVIEW</div>', unsafe_allow_html=True)
col1, col2 = st.columns([1, 1])
with col1:
    st.pyplot(ch.pie_chart_sector(df), use_container_width=True)
with col2:
    st.pyplot(ch.bar_chart_sectors(df), use_container_width=True)


# ── SECTION 2: Company Age & History ─────────────────────────────────────────
st.markdown('<div class="section-header">// COMPANY AGE & HISTORY</div>', unsafe_allow_html=True)
col3, col4 = st.columns([1, 1])
with col3:
    st.pyplot(ch.histogram_company_age(df), use_container_width=True)
with col4:
    st.pyplot(ch.scatter_founded_vs_added(df), use_container_width=True)


# ── SECTION 3: S&P 500 Timeline ───────────────────────────────────────────────
st.markdown('<div class="section-header">// S&P 500 INDEX TIMELINE</div>', unsafe_allow_html=True)
col5, col6 = st.columns([1, 1])
with col5:
    st.pyplot(ch.line_chart_additions(df), use_container_width=True)
with col6:
    st.pyplot(ch.area_chart_cumulative_additions(df), use_container_width=True)


# ── SECTION 4: Distributions ──────────────────────────────────────────────────
st.markdown('<div class="section-header">// STATISTICAL DISTRIBUTIONS</div>', unsafe_allow_html=True)
col7, col8 = st.columns([1, 1])
with col7:
    st.pyplot(ch.box_plot_age_by_sector(df), use_container_width=True)
with col8:
    st.pyplot(ch.violin_years_in_sp500(df), use_container_width=True)


# ── SECTION 5: Sub-Industry & Correlations ────────────────────────────────────
st.markdown('<div class="section-header">// SUB-INDUSTRY & CORRELATIONS</div>', unsafe_allow_html=True)
col9, col10 = st.columns([1.3, 0.7])
with col9:
    st.pyplot(ch.count_plot_sub_industries(df), use_container_width=True)
with col10:
    st.pyplot(ch.heatmap_correlation(df), use_container_width=True)


# ── SECTION 6: Bonus Bubble Chart ────────────────────────────────────────────
st.markdown('<div class="section-header">// BONUS: SECTOR BUBBLE CHART</div>', unsafe_allow_html=True)
st.pyplot(ch.bubble_chart_sector_age(df), use_container_width=True)


# ── SECTION 7: Data Table ─────────────────────────────────────────────────────
st.markdown('<div class="section-header">// RAW DATA TABLE</div>', unsafe_allow_html=True)
st.markdown(f"Showing **{len(df)}** companies after applying filters.")

display_cols = ["Symbol", "Security", "GICS Sector", "GICS Sub-Industry",
                "Headquarters Location", "Date added", "Founded_Year",
                "Company_Age", "Years_in_SP500"]
st.dataframe(
    df[display_cols].rename(columns={
        "Founded_Year": "Founded",
        "Company_Age": "Age (Yrs)",
        "Years_in_SP500": "In S&P (Yrs)",
    }),
    use_container_width=True,
    height=380,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-family:'Share Tech Mono',monospace; font-size:11px; color:#4a6a80; padding: 10px 0;">
    S&P 500 Constituents Dashboard &nbsp;·&nbsp; Exploratory Data Analysis &nbsp;·&nbsp;
    Instructor: Ali Hassan Sherazi &nbsp;·&nbsp; Due: 05-June-2026
</div>
""", unsafe_allow_html=True)
