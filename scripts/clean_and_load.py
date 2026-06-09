"""Day 2: clean Bluestock datasets, build SQLite database, and run SQL queries."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from project_paths import DATA_DB, DATA_PROCESSED, DATA_RAW, SQL_DIR, ensure_directories


DB_PATH = DATA_DB / "bluestock_mf.db"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_RAW / name)


def clean_fund_master(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["launch_date"] = pd.to_datetime(df["launch_date"], errors="coerce").dt.date
    text_columns = [
        "fund_house",
        "scheme_name",
        "category",
        "sub_category",
        "plan",
        "benchmark",
        "fund_manager",
        "risk_category",
        "sebi_category_code",
    ]
    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()
    numeric_columns = [
        "expense_ratio_pct",
        "exit_load_pct",
        "min_sip_amount",
        "min_lumpsum_amount",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.drop_duplicates(subset=["amfi_code"])


def clean_nav_history(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["amfi_code", "date", "nav"])
    df = df[df["nav"] > 0]
    df = df.drop_duplicates(subset=["amfi_code", "date"]).sort_values(["amfi_code", "date"])
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
    df["daily_return_pct"] = df["daily_return_pct"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["date_id"] = df["date"].dt.strftime("%Y-%m-%d")
    df["date"] = df["date"].dt.date
    return df[["amfi_code", "date_id", "date", "nav", "daily_return_pct"]]


def clean_aum(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_id"] = df["date"].dt.strftime("%Y-%m-%d")
    df["fund_house"] = df["fund_house"].astype(str).str.strip()
    for column in ["aum_lakh_crore", "aum_crore", "num_schemes"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=["date_id", "fund_house", "aum_crore"])
    df["date"] = df["date"].dt.date
    return df[["date_id", "date", "fund_house", "aum_lakh_crore", "aum_crore", "num_schemes"]]


def clean_monthly(df: pd.DataFrame, month_column: str = "month") -> pd.DataFrame:
    df = df.copy()
    df[month_column] = df[month_column].astype(str).str.strip()
    for column in df.columns:
        if column != month_column and df[column].dtype == "object":
            df[column] = df[column].astype(str).str.strip()
        elif column != month_column:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.drop_duplicates()


def clean_performance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["amfi_code"] = df["amfi_code"].astype(str)
    numeric_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.drop_duplicates(subset=["amfi_code"])


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["tx_id"] = [f"TX{i:06d}" for i in range(1, len(df) + 1)]
    df["investor_id"] = df["investor_id"].astype(str).str.strip()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["date_id"] = df["transaction_date"].dt.strftime("%Y-%m-%d")
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["transaction_type"] = (
        df["transaction_type"].astype(str).str.strip().str.replace("Lump sum", "Lumpsum", regex=False)
    )
    for column in ["state", "city", "city_tier", "age_group", "gender", "payment_mode", "kyc_status"]:
        df[column] = df[column].astype(str).str.strip()
    df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")
    df["annual_income_lakh"] = pd.to_numeric(df["annual_income_lakh"], errors="coerce")
    valid_types = {"SIP", "Lumpsum", "Redemption"}
    valid_kyc = {"Verified", "Pending"}
    df = df[
        df["transaction_date"].notna()
        & df["amount_inr"].gt(0)
        & df["transaction_type"].isin(valid_types)
        & df["kyc_status"].isin(valid_kyc)
    ].copy()
    df["transaction_date"] = df["transaction_date"].dt.date
    return df[
        [
            "tx_id",
            "investor_id",
            "transaction_date",
            "date_id",
            "amfi_code",
            "transaction_type",
            "amount_inr",
            "state",
            "city",
            "city_tier",
            "age_group",
            "gender",
            "annual_income_lakh",
            "payment_mode",
            "kyc_status",
        ]
    ]


def clean_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["amfi_code"] = df["amfi_code"].astype(str)
    df["portfolio_date"] = pd.to_datetime(df["portfolio_date"], errors="coerce").dt.date
    for column in ["stock_symbol", "stock_name", "sector"]:
        df[column] = df[column].astype(str).str.strip()
    for column in ["weight_pct", "market_value_cr", "current_price_inr"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    return df.dropna(subset=["amfi_code", "stock_symbol", "weight_pct"])


def clean_benchmarks(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["date_id"] = df["date"].dt.strftime("%Y-%m-%d")
    df["index_name"] = df["index_name"].astype(str).str.strip()
    df["close_value"] = pd.to_numeric(df["close_value"], errors="coerce")
    df = df.dropna(subset=["date_id", "index_name", "close_value"])
    df = df.sort_values(["index_name", "date"])
    df["daily_return_pct"] = df.groupby("index_name")["close_value"].pct_change() * 100
    df["daily_return_pct"] = df["daily_return_pct"].replace([np.inf, -np.inf], np.nan).fillna(0)
    df["date"] = df["date"].dt.date
    return df[["date_id", "date", "index_name", "close_value", "daily_return_pct"]]


def build_dim_date(*frames: pd.DataFrame) -> pd.DataFrame:
    date_values: set[str] = set()
    for frame in frames:
        if "date_id" in frame.columns:
            date_values.update(frame["date_id"].dropna().astype(str).tolist())
    dates = pd.to_datetime(sorted(date_values), errors="coerce")
    dim = pd.DataFrame({"date": dates}).dropna()
    dim["date_id"] = dim["date"].dt.strftime("%Y-%m-%d")
    dim["year"] = dim["date"].dt.year
    dim["month"] = dim["date"].dt.month
    dim["quarter"] = dim["date"].dt.quarter
    dim["month_name"] = dim["date"].dt.month_name()
    dim["is_weekday"] = dim["date"].dt.weekday.lt(5).astype(int)
    dim["date"] = dim["date"].dt.date
    return dim[["date_id", "date", "year", "month", "quarter", "month_name", "is_weekday"]]


def write_clean_csvs(cleaned: dict[str, pd.DataFrame]) -> None:
    for name, df in cleaned.items():
        df.to_csv(DATA_PROCESSED / f"clean_{name}.csv", index=False)


def load_database(cleaned: dict[str, pd.DataFrame]) -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
        cleaned["fund_master"].to_sql("dim_fund", conn, if_exists="append", index=False)
        cleaned["dim_date"].to_sql("dim_date", conn, if_exists="append", index=False)
        cleaned["nav_history"][["amfi_code", "date_id", "nav", "daily_return_pct"]].to_sql(
            "fact_nav", conn, if_exists="append", index=False
        )
        cleaned["transactions"].to_sql("fact_transactions", conn, if_exists="append", index=False)
        perf_columns = [
            "amfi_code",
            "return_1yr_pct",
            "return_3yr_pct",
            "return_5yr_pct",
            "benchmark_3yr_pct",
            "alpha",
            "beta",
            "sharpe_ratio",
            "sortino_ratio",
            "std_dev_ann_pct",
            "max_drawdown_pct",
            "aum_crore",
            "expense_ratio_pct",
            "morningstar_rating",
            "risk_grade",
        ]
        cleaned["performance"][perf_columns].to_sql("fact_performance", conn, if_exists="append", index=False)
        cleaned["portfolio"].to_sql("fact_portfolio", conn, if_exists="append", index=False)
        cleaned["aum"][["date_id", "fund_house", "aum_lakh_crore", "aum_crore", "num_schemes"]].to_sql(
            "fact_aum", conn, if_exists="append", index=False
        )
        cleaned["sip"].to_sql("fact_sip_industry", conn, if_exists="append", index=False)
        cleaned["category_inflows"].to_sql("fact_category_inflows", conn, if_exists="append", index=False)
        cleaned["folios"].to_sql("fact_industry_folios", conn, if_exists="append", index=False)
        cleaned["benchmarks"][["date_id", "index_name", "close_value", "daily_return_pct"]].to_sql(
            "fact_benchmark_indices", conn, if_exists="append", index=False
        )
        conn.commit()
    finally:
        conn.close()


def split_sql_queries(sql_text: str) -> list[tuple[str, str]]:
    queries: list[tuple[str, str]] = []
    current_title = "Query"
    current_sql: list[str] = []
    for line in sql_text.splitlines():
        if line.startswith("--"):
            if current_sql:
                queries.append((current_title, "\n".join(current_sql).strip().rstrip(";")))
                current_sql = []
            current_title = line[2:].strip()
        elif line.strip():
            current_sql.append(line)
    if current_sql:
        queries.append((current_title, "\n".join(current_sql).strip().rstrip(";")))
    return queries


def run_queries() -> None:
    conn = sqlite3.connect(DB_PATH)
    report = ["# SQL Query Results", ""]
    try:
        for title, query in split_sql_queries((SQL_DIR / "queries.sql").read_text(encoding="utf-8")):
            df = pd.read_sql_query(query, conn)
            report.extend([f"## {title}", "", df.head(20).to_markdown(index=False), ""])
    finally:
        conn.close()
    (DATA_PROCESSED / "sql_query_results.md").write_text("\n".join(report), encoding="utf-8")


def write_data_dictionary(cleaned: dict[str, pd.DataFrame]) -> None:
    sections = ["# Data Dictionary", ""]
    for name, df in cleaned.items():
        sections.extend([f"## {name}", "", "| Column | Type | Nulls |", "|---|---:|---:|"])
        for column in df.columns:
            sections.append(f"| `{column}` | `{df[column].dtype}` | {int(df[column].isna().sum())} |")
        sections.append("")
    (DATA_PROCESSED / "data_dictionary.md").write_text("\n".join(sections), encoding="utf-8")


def write_cleaning_report(raw_counts: dict[str, int], cleaned: dict[str, pd.DataFrame]) -> None:
    lines = ["# Day 2 Cleaning Report", "", "| Dataset | Raw Rows | Clean Rows |", "|---|---:|---:|"]
    for name, df in cleaned.items():
        if name == "dim_date":
            continue
        lines.append(f"| {name} | {raw_counts.get(name, 0):,} | {len(df):,} |")
    lines.extend(
        [
            "",
            "## Validation Notes",
            "",
            "- NAV values are numeric and greater than zero.",
            "- Transaction amounts are positive and transaction types are standardized to SIP, Lumpsum, and Redemption.",
            "- AMFI codes are stored as text to preserve key consistency across files.",
            "- Daily return percentages were computed for NAV and benchmark series.",
            "- SQLite database was rebuilt from the cleaned CSV outputs.",
        ]
    )
    (DATA_PROCESSED / "cleaning_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_directories()
    raw = {
        "fund_master": read_csv("01_fund_master.csv"),
        "nav_history": read_csv("02_nav_history.csv"),
        "aum": read_csv("03_aum_by_fund_house.csv"),
        "sip": read_csv("04_monthly_sip_inflows.csv"),
        "category_inflows": read_csv("05_category_inflows.csv"),
        "folios": read_csv("06_industry_folio_count.csv"),
        "performance": read_csv("07_scheme_performance.csv"),
        "transactions": read_csv("08_investor_transactions.csv"),
        "portfolio": read_csv("09_portfolio_holdings.csv"),
        "benchmarks": read_csv("10_benchmark_indices.csv"),
    }
    cleaned = {
        "fund_master": clean_fund_master(raw["fund_master"]),
        "nav_history": clean_nav_history(raw["nav_history"]),
        "aum": clean_aum(raw["aum"]),
        "sip": clean_monthly(raw["sip"]),
        "category_inflows": clean_monthly(raw["category_inflows"]),
        "folios": clean_monthly(raw["folios"]),
        "performance": clean_performance(raw["performance"]),
        "transactions": clean_transactions(raw["transactions"]),
        "portfolio": clean_portfolio(raw["portfolio"]),
        "benchmarks": clean_benchmarks(raw["benchmarks"]),
    }
    cleaned["dim_date"] = build_dim_date(
        cleaned["nav_history"], cleaned["aum"], cleaned["transactions"], cleaned["benchmarks"]
    )

    write_clean_csvs(cleaned)
    load_database(cleaned)
    run_queries()
    write_data_dictionary(cleaned)
    write_cleaning_report({key: len(value) for key, value in raw.items()}, cleaned)
    print("Day 2 cleaning and database load complete.")
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    main()
