# S&P 500 Constituents — Data Visualization Dashboard

**Course:** Exploratory Data Analysis  
**Instructor:** Ali Hassan Sherazi  
**Submission Date:** 05-June-2026

---

## Project Overview

A fully interactive Streamlit dashboard that analyzes the S&P 500 index constituents dataset. The dashboard presents **10+ chart types**, **6 interactive filters** (all linked), and **KPI summary cards** to explore sector composition, company ages, index history, and geographic distribution.

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10 or higher

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Dataset
The dataset file `constituents.txt` must be placed inside the `data/` folder exactly as provided. **Do NOT rename it.**

### 4. Run the Dashboard
```bash
streamlit run app.py
```

The dashboard opens automatically at `http://localhost:8501`.

---

## Project Structure

```
dashboard_project/
├── data/
│   └── constituents.txt          ← S&P 500 dataset (exact name preserved)
├── notebooks/
│   └── analysis.ipynb            ← EDA notebook
├── app.py                        ← Main Streamlit dashboard
├── charts.py                     ← All chart/visualization functions
├── filters.py                    ← Data loading, cleaning & filter logic
├── requirements.txt              ← Python dependencies
└── README.md                     ← This file
```

---

## Chart Types Implemented

| # | Chart Type | Insight |
|---|-----------|---------|
| 1 | **Pie Chart** | Sector proportional distribution |
| 2 | **Histogram** | Company age frequency distribution |
| 3 | **Line Chart** | Annual S&P 500 additions over time |
| 4 | **Bar Chart** | Companies per GICS sector (horizontal) |
| 5 | **Scatter Plot** | Founding year vs year added to index |
| 6 | **Box Plot** | Company age spread per sector |
| 7 | **Heatmap** | Correlation matrix of numerical features |
| 8 | **Area Chart** | Cumulative companies added over time |
| 9 | **Count Plot** | Top 15 sub-industries by count |
| 10 | **Violin Plot** | Years in S&P 500 distribution by sector |
| ★ | **Bubble Chart** (Bonus) | Sector size × avg age × sub-industry count |

---

## Filters (All Linked to Charts)

| Filter | Type | Column |
|--------|------|--------|
| GICS Sector | Multi-select | `GICS Sector` |
| Sub-Industry | Multi-select | `GICS Sub-Industry` |
| HQ Location | Multi-select | `HQ_State` |
| Year Added | Numerical Range Slider | `Year_Added` |
| Founded Year | Numerical Range Slider | `Founded_Year` |
| Company Age | Numerical Range Slider | `Company_Age` |
| Search | Text Input | Symbol, Security, HQ, Sub-Industry |
| Reset | Button | Clears all filters |

---

## Key Insights

- **Information Technology** is the largest S&P 500 sector by company count, followed by **Health Care** and **Industrials**.
- The **average S&P 500 company** was founded ~75–80 years ago, but the range spans from 1784 (BNY Mellon) to 2023.
- Most companies were added to the index in the **1990s–2000s**, with notable waves around 1997–1999 (tech boom) and 2019–2023.
- **Financials** companies tend to be the oldest on average, while **Information Technology** skews much younger.
- Strong negative correlation exists between `Founded_Year` and `Company_Age` (expected), and a moderate positive correlation between `Founded_Year` and `Year_Added`.
- **California** hosts the most S&P 500 companies, followed by **New York** and **Texas**.

---

## Technical Stack

| Tool | Role |
|------|------|
| Python 3.x | Core language |
| Pandas | Data loading, cleaning, filtering |
| NumPy | Numerical operations |
| Matplotlib | Core chart creation |
| Seaborn | Statistical visualizations |
| Streamlit | Interactive dashboard frontend |
