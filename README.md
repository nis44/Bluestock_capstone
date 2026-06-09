# Bluestock Mutual Fund Analytics Capstone

End-to-end internship capstone project for a Mutual Fund Analytics Platform.

## Scope Completed

- Day 1: Project setup, raw dataset ingestion, data quality report, live NAV fetch script.
- Day 2: Data cleaning, processed CSV outputs, SQLite schema, database load, analytical SQL queries, data dictionary.
- Day 3: Exploratory data analysis, chart exports, findings summary.

## Project Structure

```text
data/raw/          Original downloaded project CSVs and PDF
data/processed/    Cleaned CSVs and generated reports
data/db/           SQLite database output
notebooks/         Notebook-style analysis notes
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

## Notes

The source datasets are public/educational datasets supplied for the Bluestock capstone. Investment metrics and analysis in this repository are for educational purposes only and are not financial advice.
