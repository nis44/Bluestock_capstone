# Power BI Dashboard Build Guide

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
