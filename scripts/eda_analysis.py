"""Day 3: exploratory data analysis and chart exports for Bluestock MF datasets."""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from project_paths import CHARTS, DATA_PROCESSED, REPORTS, ensure_directories


warnings.filterwarnings("ignore", category=FutureWarning)
sns.set_theme(style="whitegrid", palette="Set2")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 11


def read_clean(name: str, parse_dates: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / f"clean_{name}.csv", parse_dates=parse_dates)


def savefig(name: str) -> None:
    path = CHARTS / name
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()


def nav_trend(nav: pd.DataFrame, fund: pd.DataFrame) -> None:
    top_codes = (
        fund[fund["plan"].eq("Direct")]
        .sort_values("expense_ratio_pct")
        .head(10)["amfi_code"]
        .astype(str)
        .tolist()
    )
    plot_df = nav[nav["amfi_code"].astype(str).isin(top_codes)].merge(
        fund[["amfi_code", "scheme_name"]].astype({"amfi_code": str}), on="amfi_code", how="left"
    )
    plt.figure(figsize=(13, 7))
    sns.lineplot(data=plot_df, x="date", y="nav", hue="scheme_name", linewidth=1.4)
    plt.title("NAV Trend for 10 Selected Direct Plans")
    plt.xlabel("Date")
    plt.ylabel("NAV (Rs.)")
    plt.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1))
    savefig("01_nav_trend_selected_funds.png")


def aum_growth(aum: pd.DataFrame) -> None:
    latest_houses = (
        aum.sort_values("date")
        .groupby("fund_house")
        .tail(1)
        .sort_values("aum_crore", ascending=False)
        .head(10)["fund_house"]
    )
    df = aum[aum["fund_house"].isin(latest_houses)].copy()
    df["year"] = df["date"].dt.year
    yearly = df.groupby(["year", "fund_house"], as_index=False)["aum_lakh_crore"].mean()
    plt.figure(figsize=(14, 7))
    sns.barplot(data=yearly, x="year", y="aum_lakh_crore", hue="fund_house")
    plt.title("AUM Growth by Top Fund Houses")
    plt.xlabel("Year")
    plt.ylabel("Average AUM (Rs. lakh crore)")
    plt.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1))
    savefig("02_aum_growth_by_amc.png")


def sip_trend(sip: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=sip, x="month_date", y="sip_inflow_crore", marker="o")
    latest = sip.sort_values("month_date").tail(1).iloc[0]
    plt.scatter([latest["month_date"]], [latest["sip_inflow_crore"]], color="red", zorder=4)
    plt.annotate(
        f"{latest['sip_inflow_crore']:,.0f} Cr",
        (latest["month_date"], latest["sip_inflow_crore"]),
        xytext=(-70, 18),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "red"},
    )
    plt.title("Monthly SIP Inflow Trend")
    plt.xlabel("Month")
    plt.ylabel("SIP Inflow (Rs. crore)")
    savefig("03_sip_inflow_trend.png")


def category_heatmap(category: pd.DataFrame) -> None:
    pivot = category.pivot_table(index="category", columns="month", values="net_inflow_crore", aggfunc="sum")
    plt.figure(figsize=(14, 6))
    sns.heatmap(pivot, cmap="RdYlGn", center=0, linewidths=0.3)
    plt.title("Category-wise Monthly Net Inflows")
    plt.xlabel("Month")
    plt.ylabel("Category")
    savefig("04_category_inflow_heatmap.png")


def investor_demographics(tx: pd.DataFrame) -> None:
    order = ["18-25", "26-35", "36-45", "46-55", "56+"]
    plt.figure(figsize=(9, 6))
    tx["age_group"].value_counts().reindex(order).plot(kind="pie", autopct="%1.1f%%", startangle=90)
    plt.title("Investor Age Group Distribution")
    plt.ylabel("")
    savefig("05_age_group_distribution.png")

    sip_tx = tx[tx["transaction_type"].eq("SIP")]
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=sip_tx, x="age_group", y="amount_inr", order=order)
    plt.title("SIP Amount Distribution by Age Group")
    plt.xlabel("Age Group")
    plt.ylabel("SIP Amount (Rs.)")
    savefig("06_sip_amount_by_age_group.png")


def geographic_distribution(tx: pd.DataFrame) -> None:
    by_state = tx.groupby("state", as_index=False)["amount_inr"].sum().sort_values("amount_inr", ascending=False)
    plt.figure(figsize=(12, 7))
    sns.barplot(data=by_state, y="state", x="amount_inr")
    plt.title("Transaction Amount by State")
    plt.xlabel("Total Transaction Amount (Rs.)")
    plt.ylabel("State")
    savefig("07_transaction_amount_by_state.png")

    plt.figure(figsize=(8, 6))
    tx.groupby("city_tier")["amount_inr"].sum().plot(kind="pie", autopct="%1.1f%%", startangle=90)
    plt.title("T30 vs B30 Transaction Value Split")
    plt.ylabel("")
    savefig("08_t30_b30_split.png")


def folio_growth(folios: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=folios, x="month_date", y="total_folios_crore", marker="o", label="Total")
    sns.lineplot(data=folios, x="month_date", y="equity_folios_crore", marker="o", label="Equity")
    plt.title("Mutual Fund Folio Count Growth")
    plt.xlabel("Month")
    plt.ylabel("Folios (crore)")
    savefig("09_folio_count_growth.png")


def return_correlation(nav: pd.DataFrame, fund: pd.DataFrame) -> None:
    top_codes = (
        fund[fund["category"].eq("Equity")]
        .sort_values("expense_ratio_pct")
        .head(10)["amfi_code"]
        .astype(str)
        .tolist()
    )
    nav_slice = nav[nav["amfi_code"].astype(str).isin(top_codes)]
    pivot = nav_slice.pivot(index="date", columns="amfi_code", values="daily_return_pct")
    corr = pivot.corr()
    labels = fund.set_index(fund["amfi_code"].astype(str))["scheme_name"].str.slice(0, 18)
    corr = corr.rename(index=labels.to_dict(), columns=labels.to_dict())
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, cmap="coolwarm", center=0, annot=False)
    plt.title("Daily Return Correlation Matrix")
    savefig("10_return_correlation_matrix.png")


def sector_allocation(portfolio: pd.DataFrame) -> None:
    sector = portfolio.groupby("sector", as_index=False)["weight_pct"].sum().sort_values("weight_pct", ascending=False)
    plt.figure(figsize=(10, 7))
    plt.pie(sector["weight_pct"], labels=sector["sector"], autopct="%1.1f%%", startangle=90, pctdistance=0.85)
    centre_circle = plt.Circle((0, 0), 0.55, fc="white")
    plt.gca().add_artist(centre_circle)
    plt.title("Portfolio Holdings Sector Allocation")
    savefig("11_sector_allocation_donut.png")


def performance_scatter(perf: pd.DataFrame) -> None:
    plt.figure(figsize=(11, 7))
    sns.scatterplot(
        data=perf,
        x="std_dev_ann_pct",
        y="return_3yr_pct",
        size="aum_crore",
        hue="risk_grade",
        sizes=(40, 500),
        alpha=0.75,
    )
    plt.title("Fund Return vs Risk")
    plt.xlabel("Annualized Standard Deviation (%)")
    plt.ylabel("3-Year Return (%)")
    savefig("12_return_vs_risk_scatter.png")


def benchmark_trend(bench: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 6))
    for index_name, group in bench.groupby("index_name"):
        group = group.sort_values("date")
        normalized = group["close_value"] / group["close_value"].iloc[0] * 100
        plt.plot(group["date"], normalized, label=index_name, linewidth=1.3)
    plt.title("Benchmark Indices Growth, Normalized to 100")
    plt.xlabel("Date")
    plt.ylabel("Normalized Index Value")
    plt.legend(fontsize=8)
    savefig("13_benchmark_indices_normalized.png")


def category_performance(perf: pd.DataFrame, fund: pd.DataFrame) -> None:
    df = perf.merge(fund[["amfi_code", "sub_category"]], on="amfi_code", how="left")
    agg = df.groupby("sub_category", as_index=False)["return_3yr_pct"].mean().sort_values("return_3yr_pct", ascending=False)
    plt.figure(figsize=(11, 6))
    sns.barplot(data=agg, x="return_3yr_pct", y="sub_category")
    plt.title("Average 3-Year Return by Fund Sub-Category")
    plt.xlabel("Average 3-Year Return (%)")
    plt.ylabel("Sub-Category")
    savefig("14_category_performance.png")


def transaction_volume(tx: pd.DataFrame) -> None:
    monthly = tx.groupby([tx["transaction_date"].dt.to_period("M").astype(str), "transaction_type"]).size().reset_index(name="count")
    monthly["month_date"] = pd.to_datetime(monthly["transaction_date"])
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly, x="month_date", y="count", hue="transaction_type", marker="o")
    plt.title("Monthly Transaction Volume by Type")
    plt.xlabel("Month")
    plt.ylabel("Transaction Count")
    savefig("15_monthly_transaction_volume.png")


def write_findings(
    fund: pd.DataFrame,
    nav: pd.DataFrame,
    aum: pd.DataFrame,
    sip: pd.DataFrame,
    tx: pd.DataFrame,
    perf: pd.DataFrame,
    folios: pd.DataFrame,
) -> None:
    latest_aum = aum.sort_values("date").groupby("fund_house").tail(1).sort_values("aum_crore", ascending=False).iloc[0]
    top_sharpe = perf.sort_values("sharpe_ratio", ascending=False).iloc[0]
    top_sharpe_name = fund.loc[fund["amfi_code"].eq(top_sharpe["amfi_code"]), "scheme_name"].iloc[0]
    top_state = tx.groupby("state")["amount_inr"].sum().sort_values(ascending=False)
    latest_sip = sip.sort_values("month_date").iloc[-1]
    folio_growth_pct = (
        folios.sort_values("month_date")["total_folios_crore"].iloc[-1]
        / folios.sort_values("month_date")["total_folios_crore"].iloc[0]
        - 1
    ) * 100
    category_return = (
        perf.merge(fund[["amfi_code", "sub_category"]], on="amfi_code")
        .groupby("sub_category")["return_3yr_pct"]
        .mean()
        .sort_values(ascending=False)
    )
    sip_split = tx[tx["transaction_type"].eq("SIP")].groupby("city_tier")["amount_inr"].sum()
    direct_avg_expense = fund[fund["plan"].eq("Direct")]["expense_ratio_pct"].mean()
    regular_avg_expense = fund[fund["plan"].eq("Regular")]["expense_ratio_pct"].mean()

    findings = [
        "# Day 3 EDA Findings",
        "",
        f"1. The latest AUM leader is {latest_aum['fund_house']} with Rs. {latest_aum['aum_lakh_crore']:.2f} lakh crore.",
        f"2. Monthly SIP inflow reaches Rs. {latest_sip['sip_inflow_crore']:,.0f} crore in {latest_sip['month']}.",
        f"3. Total folios grew by {folio_growth_pct:.1f}% across the available period.",
        f"4. The highest Sharpe ratio in the performance file is {top_sharpe['sharpe_ratio']:.2f} for {top_sharpe_name}.",
        f"5. {category_return.index[0]} has the highest average 3-year return at {category_return.iloc[0]:.2f}%.",
        f"6. {top_state.index[0]} contributes the highest transaction value at Rs. {top_state.iloc[0]:,.0f}.",
        f"7. SIP transaction value is split across city tiers as: {', '.join(f'{k}: Rs. {v:,.0f}' for k, v in sip_split.items())}.",
        f"8. Direct plans have a lower average expense ratio ({direct_avg_expense:.2f}%) than regular plans ({regular_avg_expense:.2f}%).",
        f"9. NAV history covers {nav['amfi_code'].nunique()} schemes and {len(nav):,} cleaned scheme-date observations.",
        f"10. Investor transaction data contains {tx['investor_id'].nunique():,} investors and {len(tx):,} validated transactions.",
        "",
        "## Exported Charts",
        "",
    ]
    for chart in sorted(CHARTS.glob("*.png")):
        findings.append(f"- `{chart.name}`")
    (REPORTS / "EDA_Findings.md").write_text("\n".join(findings), encoding="utf-8")


def write_notebook_placeholder() -> None:
    text = """# EDA Analysis Notebook

This notebook companion documents the Day 3 workflow.

Run the reproducible EDA script from the project root:

```bash
python scripts/eda_analysis.py
```

The script exports 15 chart PNG files into `reports/charts/` and writes the computed insight summary to `reports/EDA_Findings.md`.
"""
    (REPORTS / "EDA_Analysis.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_directories()
    fund = read_clean("fund_master")
    nav = read_clean("nav_history", parse_dates=["date"])
    aum = read_clean("aum", parse_dates=["date"])
    sip = read_clean("sip")
    category = read_clean("category_inflows")
    folios = read_clean("folios")
    perf = read_clean("performance")
    tx = read_clean("transactions", parse_dates=["transaction_date"])
    portfolio = read_clean("portfolio")
    bench = read_clean("benchmarks", parse_dates=["date"])

    for frame in [fund, nav, perf, tx, portfolio]:
        if "amfi_code" in frame.columns:
            frame["amfi_code"] = frame["amfi_code"].astype(str)
    sip["month_date"] = pd.to_datetime(sip["month"])
    folios["month_date"] = pd.to_datetime(folios["month"])

    nav_trend(nav, fund)
    aum_growth(aum)
    sip_trend(sip)
    category_heatmap(category)
    investor_demographics(tx)
    geographic_distribution(tx)
    folio_growth(folios)
    return_correlation(nav, fund)
    sector_allocation(portfolio)
    performance_scatter(perf)
    benchmark_trend(bench)
    category_performance(perf, fund)
    transaction_volume(tx)
    write_findings(fund, nav, aum, sip, tx, perf, folios)
    write_notebook_placeholder()
    print("Day 3 EDA complete.")
    print(f"Charts: {CHARTS}")
    print(f"Findings: {REPORTS / 'EDA_Findings.md'}")


if __name__ == "__main__":
    main()
