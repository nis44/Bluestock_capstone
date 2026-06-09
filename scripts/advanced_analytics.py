"""Day 6: advanced risk analytics, investor cohorts, and recommendation logic."""

from __future__ import annotations

import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from project_paths import CHARTS, DATA_PROCESSED, REPORTS, ROOT, ensure_directories


TRADING_DAYS = 252
RISK_FREE_RATE = 0.065


def historical_var_cvar(returns: pd.Series, confidence: float = 0.95) -> tuple[float, float]:
    threshold = np.percentile(returns.dropna(), (1 - confidence) * 100)
    tail = returns[returns <= threshold]
    return threshold * 100, tail.mean() * 100


def write_recommender_script(scorecard: pd.DataFrame) -> None:
    script = '''"""Simple fund recommender for Bluestock MF capstone."""

from __future__ import annotations

import pandas as pd


def recommend_funds(risk_appetite: str, top_n: int = 3) -> pd.DataFrame:
    risk_appetite = risk_appetite.strip().lower()
    mapping = {
        "low": ["Low"],
        "moderate": ["Moderate"],
        "high": ["High", "Very High"],
        "very high": ["Very High", "High"],
    }
    allowed = mapping.get(risk_appetite, ["Moderate"])
    scorecard = pd.read_csv("data/processed/fund_scorecard.csv")
    risk_column = "risk_category" if "risk_category" in scorecard.columns else "risk_grade"
    filtered = scorecard[scorecard[risk_column].isin(allowed)]
    if filtered.empty:
        filtered = scorecard
    columns = ["scheme_name", "fund_house", risk_column, "sharpe_ratio", "return_3yr_pct", "expense_ratio_pct", "fund_score"]
    return filtered.sort_values(["fund_score", "sharpe_ratio"], ascending=False)[columns].head(top_n)


if __name__ == "__main__":
    for appetite in ["Low", "Moderate", "High"]:
        print(f"\\nTop recommendations for {appetite} risk appetite")
        print(recommend_funds(appetite).to_string(index=False))
'''
    (ROOT / "scripts" / "recommender.py").write_text(script, encoding="utf-8")


def main() -> None:
    ensure_directories()
    sns.set_theme(style="whitegrid", palette="Set2")

    fund = pd.read_csv(DATA_PROCESSED / "clean_fund_master.csv", dtype={"amfi_code": str})
    nav = pd.read_csv(DATA_PROCESSED / "clean_nav_history.csv", parse_dates=["date"], dtype={"amfi_code": str})
    tx = pd.read_csv(DATA_PROCESSED / "clean_transactions.csv", parse_dates=["transaction_date"], dtype={"amfi_code": str})
    portfolio = pd.read_csv(DATA_PROCESSED / "clean_portfolio.csv", dtype={"amfi_code": str})
    scorecard = pd.read_csv(DATA_PROCESSED / "fund_scorecard.csv", dtype={"amfi_code": str})

    nav["daily_return"] = nav["daily_return_pct"] / 100
    var_rows = []
    for code, group in nav.groupby("amfi_code"):
        var_95, cvar_95 = historical_var_cvar(group["daily_return"], 0.95)
        var_rows.append({"amfi_code": code, "var_95_pct": var_95, "cvar_95_pct": cvar_95})
    var_report = pd.DataFrame(var_rows).merge(
        fund[["amfi_code", "scheme_name", "fund_house", "sub_category", "risk_category"]], on="amfi_code", how="left"
    )
    var_report.to_csv(DATA_PROCESSED / "var_cvar_report.csv", index=False)

    top_codes = scorecard.head(5)["amfi_code"].tolist()
    plt.figure(figsize=(13, 7))
    label_map = fund.set_index("amfi_code")["scheme_name"].str.slice(0, 28).to_dict()
    for code, group in nav[nav["amfi_code"].isin(top_codes)].groupby("amfi_code"):
        group = group.sort_values("date").copy()
        rolling = (
            (group["daily_return"].rolling(90).mean() - RISK_FREE_RATE / TRADING_DAYS)
            / group["daily_return"].rolling(90).std()
            * math.sqrt(TRADING_DAYS)
        )
        plt.plot(group["date"], rolling, label=label_map.get(code, code), linewidth=1.3)
    plt.title("Rolling 90-Day Sharpe Ratio for Top Scorecard Funds")
    plt.xlabel("Date")
    plt.ylabel("Rolling Sharpe")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(CHARTS / "17_rolling_90d_sharpe.png", dpi=160, bbox_inches="tight")
    plt.close()

    first_tx = tx.groupby("investor_id")["transaction_date"].min().rename("first_transaction_date")
    tx_cohort = tx.merge(first_tx, on="investor_id")
    tx_cohort["cohort_year"] = tx_cohort["first_transaction_date"].dt.year
    cohort = (
        tx_cohort.groupby("cohort_year")
        .agg(
            investors=("investor_id", "nunique"),
            avg_transaction_amount=("amount_inr", "mean"),
            total_invested=("amount_inr", "sum"),
            sip_transactions=("transaction_type", lambda s: int((s == "SIP").sum())),
        )
        .reset_index()
    )
    cohort.to_csv(DATA_PROCESSED / "cohort_analysis.csv", index=False)

    sip_tx = tx[tx["transaction_type"].eq("SIP")].sort_values(["investor_id", "transaction_date"])
    sip_tx["gap_days"] = sip_tx.groupby("investor_id")["transaction_date"].diff().dt.days
    continuity = (
        sip_tx.groupby("investor_id")
        .agg(
            sip_count=("transaction_date", "count"),
            avg_gap_days=("gap_days", "mean"),
            total_sip_amount=("amount_inr", "sum"),
        )
        .reset_index()
    )
    continuity = continuity[continuity["sip_count"] >= 6].copy()
    continuity["continuity_status"] = np.where(continuity["avg_gap_days"] > 35, "At Risk", "Regular")
    continuity.to_csv(DATA_PROCESSED / "sip_continuity.csv", index=False)

    sector = portfolio.groupby(["amfi_code", "sector"], as_index=False)["weight_pct"].sum()
    sector["weight_decimal"] = sector["weight_pct"] / 100
    hhi = sector.groupby("amfi_code").agg(sector_hhi=("weight_decimal", lambda s: (s**2).sum())).reset_index()
    hhi = hhi.merge(fund[["amfi_code", "scheme_name", "fund_house", "sub_category"]], on="amfi_code", how="left")
    hhi = hhi.sort_values("sector_hhi", ascending=False)
    hhi.to_csv(DATA_PROCESSED / "sector_hhi.csv", index=False)

    plt.figure(figsize=(12, 7))
    sns.barplot(data=hhi.head(15), x="sector_hhi", y="scheme_name")
    plt.title("Top 15 Funds by Sector Concentration HHI")
    plt.xlabel("Sector HHI")
    plt.ylabel("Scheme")
    plt.tight_layout()
    plt.savefig(CHARTS / "18_sector_concentration_hhi.png", dpi=160, bbox_inches="tight")
    plt.close()

    write_recommender_script(scorecard)

    high_var = var_report.sort_values("var_95_pct").iloc[0]
    at_risk_pct = (continuity["continuity_status"].eq("At Risk").mean() * 100) if len(continuity) else 0
    report = [
        "# Day 6 Advanced Analytics",
        "",
        f"1. Highest one-day 95% VaR loss is {high_var['var_95_pct']:.2f}% for {high_var['scheme_name']}.",
        f"2. SIP continuity analysis reviewed {len(continuity):,} investors with at least 6 SIP transactions.",
        f"3. {at_risk_pct:.1f}% of recurring SIP investors are flagged as at-risk using average gap > 35 days.",
        f"4. Highest sector concentration HHI is {hhi.iloc[0]['sector_hhi']:.3f} for {hhi.iloc[0]['scheme_name']}.",
        f"5. Recommendation logic ranks funds by scorecard and Sharpe within matched risk appetite.",
        "",
        "## Generated Files",
        "",
        "- `data/processed/var_cvar_report.csv`",
        "- `data/processed/cohort_analysis.csv`",
        "- `data/processed/sip_continuity.csv`",
        "- `data/processed/sector_hhi.csv`",
        "- `scripts/recommender.py`",
        "- `reports/charts/17_rolling_90d_sharpe.png`",
        "- `reports/charts/18_sector_concentration_hhi.png`",
    ]
    (REPORTS / "Advanced_Analytics.md").write_text("\n".join(report), encoding="utf-8")
    print("Day 6 advanced analytics complete.")


if __name__ == "__main__":
    main()
