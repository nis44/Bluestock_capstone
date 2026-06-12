# Bluestock Mutual Fund Analytics Capstone

End-to-end internship capstone project for a Mutual Fund Analytics Platform.

## Scope Completed

- Day 1: Project setup, raw dataset ingestion, data quality report, live NAV fetch script.
- Day 2: Data cleaning, processed CSV outputs, SQLite schema, database load, analytical SQL queries, data dictionary.
- Day 3: Exploratory data analysis, chart exports, findings summary.
- Day 4: Fund performance analytics, alpha/beta, tracking error, and scorecard.
- Day 5: Dashboard-ready extracts and Power BI build guide.
- Day 6: Advanced analytics, VaR/CVaR, rolling Sharpe, cohorts, SIP continuity, sector HHI, recommender.
- Day 7: Final PDF report, PowerPoint deck, and submission checklist.

## Project Structure

```text
data/raw/          Original downloaded project CSVs and PDF
data/processed/    Cleaned CSVs and generated reports
data/db/           SQLite database output
notebooks/         Full code notebooks with embedded script implementations
scripts/           Python ETL and analytics scripts
sql/               Database schema and analytical queries
reports/           Markdown reports and exported charts
dashboard/         Reserved for Power BI/Tableau work
```

## Setup

```bash
python -m pip install -r requirements.txt
```

## Run Days 1-3

```bash
python scripts/data_ingestion.py
python scripts/live_nav_fetch.py
python scripts/clean_and_load.py
python scripts/eda_analysis.py
python scripts/compute_metrics.py
python scripts/advanced_analytics.py
python scripts/prepare_dashboard.py
python scripts/generate_final_assets.py
```

## Main Outputs

- `data/processed/data_quality_report.md`
- `data/processed/clean_*.csv`
- `data/db/bluestock_mf.db`
- `sql/schema.sql`
- `sql/queries.sql`
- `data/processed/sql_query_results.md`
- `data/processed/data_dictionary.md`
- `reports/EDA_Findings.md`
- `reports/charts/*.png`
- `data/processed/fund_scorecard.csv`
- `data/processed/var_cvar_report.csv`
- `dashboard/extracts/*.csv`
- `dashboard/PowerBI_Dashboard_Build_Guide.md`
- `reports/Final_Report.pdf`
- `reports/Bluestock_MF_Presentation.pptx`

## Notes

The source datasets are public/educational datasets supplied for the Bluestock capstone. Investment metrics and analysis in this repository are for educational purposes only and are not financial advice.
