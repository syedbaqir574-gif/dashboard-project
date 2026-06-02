"""
filters.py — Data loading, cleaning, and filtering functions
S&P 500 Constituents Dashboard
"""

import pandas as pd
import numpy as np
import re


def load_data(filepath: str = "data/constituents.txt") -> pd.DataFrame:
    """Load and clean the S&P 500 constituents dataset."""
    df = pd.read_csv(filepath)

    # ── Clean column names ──────────────────────────────────────────────────
    df.columns = df.columns.str.strip()

    # ── Parse 'Founded' year (may contain notes like '2013 (1888)') ─────────
    def extract_year(val):
        if pd.isna(val):
            return np.nan
        match = re.search(r"\b(\d{4})\b", str(val))
        return int(match.group(1)) if match else np.nan

    df["Founded_Year"] = df["Founded"].apply(extract_year)

    # ── Parse 'Date added' as datetime ──────────────────────────────────────
    df["Date added"] = pd.to_datetime(df["Date added"], errors="coerce")
    df["Year_Added"] = df["Date added"].dt.year

    # ── Derived: Company Age (years since founding) ─────────────────────────
    current_year = 2026
    df["Company_Age"] = current_year - df["Founded_Year"]

    # ── Derived: Years in S&P 500 ───────────────────────────────────────────
    df["Years_in_SP500"] = current_year - df["Year_Added"]

    # ── Strip whitespace from string columns ───────────────────────────────
    for col in ["Symbol", "Security", "GICS Sector", "GICS Sub-Industry",
                "Headquarters Location"]:
        df[col] = df[col].astype(str).str.strip()

    # ── Headquarters state extraction ──────────────────────────────────────
    def extract_state(loc):
        parts = str(loc).split(",")
        if len(parts) >= 2:
            return parts[-1].strip()
        return "Unknown"

    df["HQ_State"] = df["Headquarters Location"].apply(extract_state)

    return df


def apply_filters(
    df: pd.DataFrame,
    sectors: list = None,
    sub_industries: list = None,
    year_added_range: tuple = None,
    founded_range: tuple = None,
    age_range: tuple = None,
    search_text: str = "",
    states: list = None,
) -> pd.DataFrame:
    """
    Apply all sidebar filters to the dataframe and return filtered result.
    All charts must be fed from this single function so filters stay linked.
    """
    filtered = df.copy()

    # Category filter: GICS Sector
    if sectors:
        filtered = filtered[filtered["GICS Sector"].isin(sectors)]

    # Multi-select filter: Sub-Industry
    if sub_industries:
        filtered = filtered[filtered["GICS Sub-Industry"].isin(sub_industries)]

    # Multi-select filter: HQ State
    if states:
        filtered = filtered[filtered["HQ_State"].isin(states)]

    # Numerical range slider: Year Added
    if year_added_range:
        lo, hi = year_added_range
        filtered = filtered[
            (filtered["Year_Added"] >= lo) & (filtered["Year_Added"] <= hi)
        ]

    # Numerical range slider: Founded Year
    if founded_range:
        lo, hi = founded_range
        filtered = filtered[
            (filtered["Founded_Year"] >= lo) & (filtered["Founded_Year"] <= hi)
        ]

    # Numerical range slider: Company Age
    if age_range:
        lo, hi = age_range
        filtered = filtered[
            (filtered["Company_Age"] >= lo) & (filtered["Company_Age"] <= hi)
        ]

    # Search / Text filter
    if search_text.strip():
        q = search_text.strip().lower()
        mask = (
            filtered["Symbol"].str.lower().str.contains(q, na=False)
            | filtered["Security"].str.lower().str.contains(q, na=False)
            | filtered["Headquarters Location"].str.lower().str.contains(q, na=False)
            | filtered["GICS Sub-Industry"].str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]

    return filtered.reset_index(drop=True)
