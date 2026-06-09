"""Prepare dashboard-ready CSV extracts and a Power BI build guide."""

from __future__ import annotations

import pandas as pd

from project_paths import DATA_PROCESSED, ROOT, ensure_directories


def main() -> None:
    ensure_directories()
    dashboard_dir = ROOT / "dashboard"
    extracts = dashboard_dir / "extracts"
    extracts.mkdir(parents=True, exist_ok=True)

    files = [
        "clean_fund_master.csv",
        "clean_nav_history.csv",
        "clean_aum.csv",
        "clean_sip.csv",
        "clean_category_inflows.csv",
        "clean_folios.csv",
        "clean_transactions.csv",
        "clean_portfolio.csv",
        "clean_benchmarks.csv",
        "fund_scorecard.csv",
        "var_cvar_report.csv",
        "cohort_analysis.csv",
        "sip_continuity.csv",
        "sector_hhi.csv",
    ]
    for filename in files:
        src = DATA_PROCESSED / filename
        if src.exists():
            pd.read_csv(src).to_csv(extracts / filename, index=False)

    guide = """# Power BI Dashboard Build Guide

Power BI Desktop cannot be reliably automated from this environment, so this folder contains clean dashboard-ready extracts and a page-by-page build guide.

## Data Source

Use `dashboard/extracts/*.csv` or connect to `data/db/bluestock_mf.db`.

## Page 1: Industry Overview

- KPI cards: latest AUM, latest SIP inflow, latest folio count, number of schemes.
- Line chart: SIP inflow by month.
- Bar chart: latest AUM by fund house.
- Slicers: date/month, fund house.

## Page 2: Fund Performance

- Scatter: `std_dev_ann_pct` vs `return_3yr_pct`, bubble size `fund_score`.
- Table: scheme, fund house, Sharpe, alpha, beta, max drawdown, fund score.
- Line chart: selected fund NAV vs benchmark.
- Slicers: fund house, category, sub-category, plan.

## Page 3: Investor Analytics

- Bar/map: transaction amount by state.
- Donut: SIP/Lumpsum/Redemption split.
- Bar: average SIP amount by age group.
- Line: monthly transaction volume.
- Slicers: state, city tier, age group, transaction type.

## Page 4: SIP and Market Trends

- Combo chart: SIP inflow and NIFTY50 normalized trend.
- Heatmap: category inflows by month.
- Bar: top categories by net inflow.
- KPI: SIP account growth.

## Branding

Use a restrained finance palette: white background, dark text, teal accents, amber highlights for milestones, red only for drawdown/risk.
"""
    (dashboard_dir / "PowerBI_Dashboard_Build_Guide.md").write_text(guide, encoding="utf-8")
    print("Dashboard extracts and Power BI guide complete.")


if __name__ == "__main__":
    main()
