import os
import streamlit as st
import pandas as pd
import numpy as np
from filters import load_data, apply_filters
import charts as ch

st.set_page_config(page_title="S&P 500 Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');
:root{--bg:#0f1923;--card:#162433;--accent:#2ea8cc;--text:#e8edf2;--muted:#7a99b0;--border:#243447}
html,body,[class*="css"]{background-color:var(--bg);color:var(--text);font-family:'Rajdhani',sans-serif}
section[data-testid="stSidebar"]{background-color:#0d1620!important;border-right:1px solid var(--border)}
section[data-testid="stSidebar"] *{color:var(--text)!important}
.kpi-card{background:var(--card);border:1px solid var(--border);border-top:3px solid var(--accent);border-radius:8px;padding:18px 20px 14px;text-align:center;margin-bottom:4px}
.kpi-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:6px}
.kpi-value{font-size:32px;font-weight:700;color:var(--accent);line-height:1}
.kpi-sub{font-size:11px;color:var(--muted);margin-top:4px}
.section-header{font-size:11px;color:var(--accent);text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid var(--border);padding-bottom:6px;margin:22px 0 14px}
.stButton>button{background:var(--accent)!important;color:#0f1923!important;border:none!important;font-weight:700!important;border-radius:4px!important}
#MainMenu,footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def get_data():
    return load_data()


df_raw = get_data()

with st.sidebar:
    st.markdown("## Filters")
    st.markdown("---")
    if st.button("Reset All Filters"):
        st.session_state.clear()
        st.rerun()
    all_sectors = sorted(df_raw["GICS Sector"].dropna().unique().tolist())
    selected_sectors = st.multiselect("Sector", options=all_sectors, default=[], key="sectors")
    if selected_sectors:
        sub_pool = df_raw[df_raw["GICS Sector"].isin(selected_sectors)]["GICS Sub-Industry"]
    else:
        sub_pool = df_raw["GICS Sub-Industry"]
    selected_subs = st.multiselect("Sub-Industry", options=sorted(sub_pool.dropna().unique().tolist()), default=[], key="subs")
    all_states = sorted(df_raw["HQ_State"].dropna().unique().tolist())
    selected_states = st.multiselect("HQ Location", options=all_states, default=[], key="states")
    min_ya, max_ya = int(df_raw["Year_Added"].min()), int(df_raw["Year_Added"].max())
    year_added_range = st.slider("Year Added", min_value=min_ya, max_value=max_ya, value=(min_ya, max_ya), key="year_added")
    min_fy, max_fy = int(df_raw["Founded_Year"].dropna().min()), int(df_raw["Founded_Year"].dropna().max())
    founded_range = st.slider("Founded Year", min_value=min_fy, max_value=max_fy, value=(min_fy, max_fy), key="founded")
    min_age, max_age = int(df_raw["Company_Age"].dropna().min()), int(df_raw["Company_Age"].dropna().max())
    age_range = st.slider("Company Age", min_value=min_age, max_value=max_age, value=(min_age, max_age), key="age")
    search_text = st.text_input("Search", value="", key="search", placeholder="e.g. Apple, Tech, California...")

df = apply_filters(df_raw, sectors=selected_sectors or None, sub_industries=selected_subs or None,
                   year_added_range=year_added_range, founded_range=founded_range,
                   age_range=age_range, search_text=search_text, states=selected_states or None)

st.markdown("## S&P 500 Constituents Dashboard")
st.markdown("Analyze S&P 500 companies by sector, founding year, geography, and index tenure.")
st.markdown("---")

st.markdown("### Key Metrics")
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Companies</div><div class="kpi-value">{len(df):,}</div><div class="kpi-sub">of {len(df_raw)} total</div></div>', unsafe_allow_html=True)
with k2:
    avg_age = df["Company_Age"].dropna().mean()
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg Company Age</div><div class="kpi-value">{avg_age:.0f}</div><div class="kpi-sub">years since founding</div></div>', unsafe_allow_html=True)
with k3:
    oldest = df.loc[df["Company_Age"].idxmax()] if len(df) > 0 else None
    oldest_name = oldest["Security"][:16] if oldest is not None else "n/a"
    oldest_age = int(oldest["Company_Age"]) if oldest is not None else 0
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Oldest Company</div><div class="kpi-value" style="font-size:18px">{oldest_name}</div><div class="kpi-sub">{oldest_age} yrs</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Sectors</div><div class="kpi-value">{df["GICS Sector"].nunique()}</div><div class="kpi-sub">GICS sectors</div></div>', unsafe_allow_html=True)
with k5:
    avg_tenure = df["Years_in_SP500"].dropna().mean()
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Avg S&P Tenure</div><div class="kpi-value">{avg_tenure:.0f}</div><div class="kpi-sub">years in index</div></div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("### Sector Overview")
c1, c2 = st.columns(2)
with c1: st.pyplot(ch.pie_chart_sector(df), use_container_width=True)
with c2: st.pyplot(ch.bar_chart_sectors(df), use_container_width=True)

st.markdown("### Company Age and History")
c3, c4 = st.columns(2)
with c3: st.pyplot(ch.histogram_company_age(df), use_container_width=True)
with c4: st.pyplot(ch.scatter_founded_vs_added(df), use_container_width=True)

st.markdown("### S&P 500 Index Timeline")
c5, c6 = st.columns(2)
with c5: st.pyplot(ch.line_chart_additions(df), use_container_width=True)
with c6: st.pyplot(ch.area_chart_cumulative_additions(df), use_container_width=True)

st.markdown("### Statistical Distributions")
c7, c8 = st.columns(2)
with c7: st.pyplot(ch.box_plot_age_by_sector(df), use_container_width=True)
with c8: st.pyplot(ch.violin_years_in_sp500(df), use_container_width=True)

st.markdown("### Sub-Industry and Correlations")
c9, c10 = st.columns([1.3, 0.7])
with c9: st.pyplot(ch.count_plot_sub_industries(df), use_container_width=True)
with c10: st.pyplot(ch.heatmap_correlation(df), use_container_width=True)

st.markdown("### Bonus Bubble Chart")
st.pyplot(ch.bubble_chart_sector_age(df), use_container_width=True)

st.markdown("### Raw Data Table")
st.markdown(f"Showing **{len(df)}** companies after filters.")
display_cols = ["Symbol", "Security", "GICS Sector", "GICS Sub-Industry", "Headquarters Location", "Date added", "Founded_Year", "Company_Age", "Years_in_SP500"]
st.dataframe(df[display_cols].rename(columns={"Founded_Year": "Founded", "Company_Age": "Age (Yrs)", "Years_in_SP500": "In S&P (Yrs)"}), use_container_width=True, height=380)

st.markdown("---")
st.markdown("Syed Baqir Hussain Shah | SAP: 70143947 | EDA |")
