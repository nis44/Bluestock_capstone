"""Day 1: ingest and validate the raw Bluestock mutual fund datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from project_paths import DATA_PROCESSED, DATA_RAW, ensure_directories


EXPECTED_DATASETS = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]


def load_raw_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def profile_dataframe(name: str, df: pd.DataFrame) -> str:
    lines = [
        f"## {name}",
        "",
        f"- Rows: {len(df):,}",
        f"- Columns: {len(df.columns):,}",
        f"- Duplicate rows: {df.duplicated().sum():,}",
        "- Column dtypes:",
    ]
    for column, dtype in df.dtypes.items():
        null_count = int(df[column].isna().sum())
        lines.append(f"  - `{column}`: {dtype}, nulls={null_count:,}")
    lines.append("")
    lines.append("Sample:")
    lines.append("")
    lines.append(df.head(5).to_markdown(index=False))
    lines.append("")
    return "\n".join(lines)


def validate_amfi_codes(fund_master: pd.DataFrame, nav_history: pd.DataFrame) -> pd.DataFrame:
    master_codes = pd.Series(fund_master["amfi_code"].astype(str).unique(), name="amfi_code")
    nav_codes = set(nav_history["amfi_code"].astype(str).unique())
    return pd.DataFrame(
        {
            "amfi_code": master_codes,
            "exists_in_nav_history": master_codes.isin(nav_codes),
        }
    )


def main() -> None:
    ensure_directories()
    report_parts = ["# Day 1 Data Ingestion Report", ""]
    loaded: dict[str, pd.DataFrame] = {}

    missing = [name for name in EXPECTED_DATASETS if not (DATA_RAW / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required raw datasets: {missing}")

    for name in EXPECTED_DATASETS:
        df = load_raw_dataset(DATA_RAW / name)
        loaded[name] = df
        report_parts.append(profile_dataframe(name, df))

    fund_master = loaded["01_fund_master.csv"]
    nav_history = loaded["02_nav_history.csv"]
    code_validation = validate_amfi_codes(fund_master, nav_history)
    code_validation.to_csv(DATA_PROCESSED / "amfi_code_validation.csv", index=False)

    report_parts.extend(
        [
            "## Fund Master Summary",
            "",
            f"- Unique fund houses: {fund_master['fund_house'].nunique():,}",
            f"- Categories: {', '.join(sorted(fund_master['category'].dropna().unique()))}",
            f"- Sub-categories: {', '.join(sorted(fund_master['sub_category'].dropna().unique()))}",
            f"- Risk categories: {', '.join(sorted(fund_master['risk_category'].dropna().unique()))}",
            "",
            "## AMFI Code Validation",
            "",
            f"- Codes in fund master: {len(code_validation):,}",
            f"- Codes found in NAV history: {int(code_validation['exists_in_nav_history'].sum()):,}",
            f"- Missing from NAV history: {int((~code_validation['exists_in_nav_history']).sum()):,}",
            "",
        ]
    )

    (DATA_PROCESSED / "data_quality_report.md").write_text(
        "\n".join(report_parts), encoding="utf-8"
    )
    print("Day 1 ingestion complete.")
    print(f"Report: {DATA_PROCESSED / 'data_quality_report.md'}")


if __name__ == "__main__":
    main()
