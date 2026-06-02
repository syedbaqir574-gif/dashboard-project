"""
filters.py — Data loading, cleaning, and filtering functions
S&P 500 Constituents Dashboard
Student: Syed Baqir Hussain Shah | SAP ID: 70177654
"""

import pandas as pd
import numpy as np
import re
import os


def load_data(filepath=None) -> pd.DataFrame:
    """Load and clean the S&P 500 constituents dataset."""
    
    # Try multiple possible paths
    possible_paths = [
        filepath,
        "data/constituents.txt",
        "constituents.txt",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "constituents.txt"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "constituents.txt"),
    ]
    
    df = None
    for path in possible_paths:
        if path and os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except:
                continue
    
    if df is None:
        raise FileNotFoundError("constituents.txt not found. Please ensure the file is in the data/ folder.")

    df.columns = df.columns.str.strip()

    def extract_year(val):
        if pd.isna(val):
            return np.nan
        match = re.search(r"\b(\d{4})\b", str(val))
        return int(match.group(1)) if match else np.nan

    df["Founded_Year"] = df["Founded"].apply(extract_year)
    df["Date added"] = pd.to_datetime(df["Date added"], errors="coerce")
    df["Year_Added"] = df["Date added"].dt.year

    current_year = 2026
    df["Company_Age"] = current_year - df["Founded_Year"]
    df["Years_in_SP500"] = current_year - df["Year_Added"]

    for col in ["Symbol", "Security", "GICS Sector", "GICS Sub-Industry", "Headquarters Location"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    def extract_state(loc):
        parts = str(loc).split(",")
        if len(parts) >= 2:
            return parts[-1].strip()
        return "Unknown"

    df["HQ_State"] = df["Headquarters Location"].apply(extract_state)

    return df


def apply_filters(
    df: pd.DataFrame,
    sectors=None,
    sub_industries=None,
    year_added_range=None,
    founded_range=None,
    age_range=None,
    search_text="",
    states=None,
) -> pd.DataFrame:
    filtered = df.copy()

    if sectors:
        filtered = filtered[filtered["GICS Sector"].isin(sectors)]
    if sub_industries:
        filtered = filtered[filtered["GICS Sub-Industry"].isin(sub_industries)]
    if states:
        filtered = filtered[filtered["HQ_State"].isin(states)]
    if year_added_range:
        lo, hi = year_added_range
        filtered = filtered[(filtered["Year_Added"] >= lo) & (filtered["Year_Added"] <= hi)]
    if founded_range:
        lo, hi = founded_range
        filtered = filtered[(filtered["Founded_Year"] >= lo) & (filtered["Founded_Year"] <= hi)]
    if age_range:
        lo, hi = age_range
        filtered = filtered[(filtered["Company_Age"] >= lo) & (filtered["Company_Age"] <= hi)]
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
