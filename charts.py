"""
charts.py — Chart & visualization functions
S&P 500 Constituents Dashboard
Uses Matplotlib + Seaborn as required. Each function accepts a filtered DataFrame
and returns a Matplotlib Figure for display in Streamlit.
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

# ── Global style ─────────────────────────────────────────────────────────────
PALETTE = [
    "#1a6b8a", "#2ea8cc", "#f2b705", "#e85d04", "#6a0572",
    "#3d9970", "#ff4136", "#b10dc9", "#01ff70", "#ff69b4",
    "#7fdbff", "#f08030",
]
BG_COLOR    = "#0f1923"
CARD_COLOR  = "#162433"
TEXT_COLOR  = "#e8edf2"
ACCENT      = "#2ea8cc"
GRID_COLOR  = "#243447"

sns.set_theme(style="darkgrid", rc={
    "axes.facecolor":   CARD_COLOR,
    "figure.facecolor": BG_COLOR,
    "axes.labelcolor":  TEXT_COLOR,
    "xtick.color":      TEXT_COLOR,
    "ytick.color":      TEXT_COLOR,
    "axes.edgecolor":   GRID_COLOR,
    "grid.color":       GRID_COLOR,
    "text.color":       TEXT_COLOR,
    "axes.titlecolor":  TEXT_COLOR,
    "legend.facecolor": CARD_COLOR,
    "legend.edgecolor": GRID_COLOR,
})

matplotlib.rcParams.update({
    "font.family": "monospace",
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


def _style_fig(fig, ax_or_axes=None):
    """Apply consistent background & spine styling."""
    fig.patch.set_facecolor(BG_COLOR)
    axes = [ax_or_axes] if ax_or_axes is not None and not hasattr(ax_or_axes, '__iter__') else ax_or_axes
    if axes:
        for ax in (axes if hasattr(axes, '__iter__') else [axes]):
            ax.set_facecolor(CARD_COLOR)
            for spine in ax.spines.values():
                spine.set_color(GRID_COLOR)


# ─────────────────────────────────────────────────────────────────────────────
# 1. PIE CHART — Sector distribution
# ─────────────────────────────────────────────────────────────────────────────
def pie_chart_sector(df: pd.DataFrame) -> plt.Figure:
    counts = df["GICS Sector"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 5))
    _style_fig(fig, ax)
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE[:len(counts)],
        startangle=140,
        wedgeprops=dict(edgecolor=BG_COLOR, linewidth=1.5),
        pctdistance=0.82,
    )
    for t in texts:
        t.set_color(TEXT_COLOR)
        t.set_fontsize(8)
    for at in autotexts:
        at.set_color(BG_COLOR)
        at.set_fontsize(7)
        at.set_fontweight("bold")
    ax.set_title("Sector Distribution of S&P 500 Companies", pad=14, fontweight="bold")
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 2. HISTOGRAM — Company Age distribution
# ─────────────────────────────────────────────────────────────────────────────
def histogram_company_age(df: pd.DataFrame) -> plt.Figure:
    ages = df["Company_Age"].dropna()
    fig, ax = plt.subplots(figsize=(7, 4))
    _style_fig(fig, ax)
    ax.hist(ages, bins=30, color=ACCENT, edgecolor=BG_COLOR, linewidth=0.6, alpha=0.9)
    ax.set_title("Distribution of Company Ages (Years Since Founding)", fontweight="bold")
    ax.set_xlabel("Company Age (Years)")
    ax.set_ylabel("Number of Companies")
    ax.axvline(ages.mean(), color="#f2b705", linestyle="--", linewidth=1.5, label=f"Mean: {ages.mean():.0f} yrs")
    ax.legend()
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 3. LINE CHART — Companies added to S&P 500 over time
# ─────────────────────────────────────────────────────────────────────────────
def line_chart_additions(df: pd.DataFrame) -> plt.Figure:
    yearly = df.groupby("Year_Added").size().reset_index(name="Count")
    yearly = yearly.dropna().sort_values("Year_Added")
    fig, ax = plt.subplots(figsize=(8, 4))
    _style_fig(fig, ax)
    ax.plot(yearly["Year_Added"], yearly["Count"], color=ACCENT, linewidth=2.2,
            marker="o", markersize=4, markerfacecolor="#f2b705", markeredgewidth=0)
    ax.fill_between(yearly["Year_Added"], yearly["Count"], alpha=0.15, color=ACCENT)
    ax.set_title("Companies Added to S&P 500 Per Year", fontweight="bold")
    ax.set_xlabel("Year Added")
    ax.set_ylabel("Number of Additions")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 4. BAR CHART — Top 12 sectors by company count
# ─────────────────────────────────────────────────────────────────────────────
def bar_chart_sectors(df: pd.DataFrame) -> plt.Figure:
    counts = df["GICS Sector"].value_counts().head(12)
    fig, ax = plt.subplots(figsize=(8, 5))
    _style_fig(fig, ax)
    bars = ax.barh(counts.index[::-1], counts.values[::-1],
                   color=PALETTE[:len(counts)], edgecolor=BG_COLOR, linewidth=0.5)
    for bar, val in zip(bars, counts.values[::-1]):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", ha="left", color=TEXT_COLOR, fontsize=9)
    ax.set_title("Companies per GICS Sector", fontweight="bold")
    ax.set_xlabel("Number of Companies")
    ax.set_ylabel("")
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 5. SCATTER PLOT — Founded Year vs Year Added
# ─────────────────────────────────────────────────────────────────────────────
def scatter_founded_vs_added(df: pd.DataFrame) -> plt.Figure:
    sub = df.dropna(subset=["Founded_Year", "Year_Added"]).copy()
    sectors = sub["GICS Sector"].unique()
    color_map = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(sectors)}
    fig, ax = plt.subplots(figsize=(8, 5))
    _style_fig(fig, ax)
    for sector, group in sub.groupby("GICS Sector"):
        ax.scatter(group["Founded_Year"], group["Year_Added"],
                   label=sector, color=color_map[sector],
                   alpha=0.75, s=30, edgecolors="none")
    ax.set_title("Founding Year vs Year Added to S&P 500", fontweight="bold")
    ax.set_xlabel("Year Founded")
    ax.set_ylabel("Year Added to S&P 500")
    ax.legend(fontsize=7, ncol=2, framealpha=0.6)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 6. BOX PLOT — Company Age by Sector
# ─────────────────────────────────────────────────────────────────────────────
def box_plot_age_by_sector(df: pd.DataFrame) -> plt.Figure:
    sub = df.dropna(subset=["Company_Age"])
    top_sectors = sub["GICS Sector"].value_counts().head(10).index.tolist()
    sub = sub[sub["GICS Sector"].isin(top_sectors)]
    order = sub.groupby("GICS Sector")["Company_Age"].median().sort_values(ascending=False).index

    fig, ax = plt.subplots(figsize=(10, 5))
    _style_fig(fig, ax)
    sns.boxplot(
        data=sub, x="GICS Sector", y="Company_Age",
        order=order, palette=PALETTE[:len(order)],
        flierprops=dict(marker="o", markersize=3, alpha=0.5, color=ACCENT),
        ax=ax
    )
    ax.set_title("Company Age Distribution by Sector", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Company Age (Years)")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 7. HEATMAP — Correlation matrix
# ─────────────────────────────────────────────────────────────────────────────
def heatmap_correlation(df: pd.DataFrame) -> plt.Figure:
    num_cols = ["Founded_Year", "Year_Added", "Company_Age", "Years_in_SP500"]
    corr = df[num_cols].dropna().corr()

    fig, ax = plt.subplots(figsize=(6, 5))
    _style_fig(fig, ax)
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        linewidths=0.5, linecolor=BG_COLOR,
        ax=ax, vmin=-1, vmax=1,
        annot_kws={"size": 11},
        cbar_kws={"shrink": 0.8},
    )
    ax.set_title("Correlation Heatmap — Numerical Features", fontweight="bold")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 8. AREA CHART — Cumulative additions over time
# ─────────────────────────────────────────────────────────────────────────────
def area_chart_cumulative_additions(df: pd.DataFrame) -> plt.Figure:
    yearly = df.dropna(subset=["Year_Added"]).groupby("Year_Added").size()
    cumulative = yearly.sort_index().cumsum()

    fig, ax = plt.subplots(figsize=(8, 4))
    _style_fig(fig, ax)
    ax.fill_between(cumulative.index, cumulative.values, alpha=0.35, color=ACCENT)
    ax.plot(cumulative.index, cumulative.values, color=ACCENT, linewidth=2)
    ax.set_title("Cumulative Companies Added to S&P 500 Over Time", fontweight="bold")
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Count")
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 9. COUNT PLOT — Top 15 sub-industries
# ─────────────────────────────────────────────────────────────────────────────
def count_plot_sub_industries(df: pd.DataFrame) -> plt.Figure:
    top = df["GICS Sub-Industry"].value_counts().head(15)
    fig, ax = plt.subplots(figsize=(9, 5))
    _style_fig(fig, ax)
    sns.barplot(x=top.values, y=top.index, palette=PALETTE[:15], ax=ax, orient="h")
    ax.set_title("Top 15 Sub-Industries by Company Count", fontweight="bold")
    ax.set_xlabel("Number of Companies")
    ax.set_ylabel("")
    for p in ax.patches:
        ax.annotate(f" {int(p.get_width())}",
                    (p.get_width(), p.get_y() + p.get_height() / 2),
                    va="center", color=TEXT_COLOR, fontsize=8)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# 10. VIOLIN PLOT — Years in S&P 500 by Sector
# ─────────────────────────────────────────────────────────────────────────────
def violin_years_in_sp500(df: pd.DataFrame) -> plt.Figure:
    sub = df.dropna(subset=["Years_in_SP500"])
    top_sectors = sub["GICS Sector"].value_counts().head(8).index.tolist()
    sub = sub[sub["GICS Sector"].isin(top_sectors)]

    fig, ax = plt.subplots(figsize=(10, 5))
    _style_fig(fig, ax)
    sns.violinplot(
        data=sub, x="GICS Sector", y="Years_in_SP500",
        palette=PALETTE[:8], inner="quartile",
        linewidth=1.0, ax=ax
    )
    ax.set_title("Years in S&P 500 Distribution by Sector (Violin Plot)", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Years in S&P 500")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha="right", fontsize=8)
    fig.tight_layout()
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# BONUS — Bubble Chart: Sector size vs avg age, bubble = sub-industry count
# ─────────────────────────────────────────────────────────────────────────────
def bubble_chart_sector_age(df: pd.DataFrame) -> plt.Figure:
    grouped = df.dropna(subset=["Company_Age"]).groupby("GICS Sector").agg(
        count=("Symbol", "count"),
        avg_age=("Company_Age", "mean"),
        sub_count=("GICS Sub-Industry", "nunique")
    ).reset_index()

    fig, ax = plt.subplots(figsize=(9, 6))
    _style_fig(fig, ax)
    scatter = ax.scatter(
        grouped["avg_age"], grouped["count"],
        s=grouped["sub_count"] * 60,
        c=range(len(grouped)), cmap="plasma",
        alpha=0.80, edgecolors=BG_COLOR, linewidths=0.8
    )
    for _, row in grouped.iterrows():
        ax.annotate(row["GICS Sector"],
                    (row["avg_age"], row["count"]),
                    textcoords="offset points", xytext=(5, 4),
                    fontsize=7.5, color=TEXT_COLOR)
    ax.set_title("Sector Bubble Chart: Avg Company Age vs # Companies\n(Bubble size = # Sub-Industries)",
                 fontweight="bold")
    ax.set_xlabel("Average Company Age (Years)")
    ax.set_ylabel("Number of Companies")
    fig.tight_layout()
    return fig
