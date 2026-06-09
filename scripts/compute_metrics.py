"""Day 4: compute fund performance metrics, scorecards, and benchmark comparisons."""

from __future__ import annotations

import math
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import linregress

from project_paths import CHARTS, DATA_PROCESSED, REPORTS, ensure_directories


warnings.filterwarnings("ignore", category=RuntimeWarning)
TRADING_DAYS = 252
RISK_FREE_RATE = 0.065


def annualized_return(returns: pd.Series) -> float:
    returns = returns.dropna()
    if returns.empty:
        return np.nan
    total = (1 + returns).prod()
    return total ** (TRADING_DAYS / len(returns)) - 1


def cagr_from_nav(group: pd.DataFrame, years: int) -> float:
    group = group.sort_values("date")
    end_date = group["date"].max()
    start_cutoff = end_date - pd.DateOffset(years=years)
    window = group[group["date"] >= start_cutoff]
    if len(window) < 2:
        return np.nan
    actual_years = (window["date"].iloc[-1] - window["date"].iloc[0]).days / 365.25
    if actual_years <= 0:
        return np.nan
    return (window["nav"].iloc[-1] / window["nav"].iloc[0]) ** (1 / actual_years) - 1


def sharpe_ratio(daily_returns: pd.Series) -> float:
    daily_returns = daily_returns.dropna()
    if daily_returns.std() == 0 or daily_returns.empty:
        return np.nan
    excess_daily = daily_returns - (RISK_FREE_RATE / TRADING_DAYS)
    return math.sqrt(TRADING_DAYS) * excess_daily.mean() / daily_returns.std()


def sortino_ratio(daily_returns: pd.Series) -> float:
    daily_returns = daily_returns.dropna()
    downside = daily_returns[daily_returns < 0]
    if downside.std() == 0 or downside.empty:
        return np.nan
    excess_daily = daily_returns - (RISK_FREE_RATE / TRADING_DAYS)
    return math.sqrt(TRADING_DAYS) * excess_daily.mean() / downside.std()


def max_drawdown(nav: pd.Series) -> float:
    running_max = nav.cummax()
    drawdown = nav / running_max - 1
    return drawdown.min()


def alpha_beta(fund_returns: pd.Series, benchmark_returns: pd.Series) -> tuple[float, float, float, float]:
    aligned = pd.concat([fund_returns, benchmark_returns], axis=1, join="inner").dropna()
    aligned.columns = ["fund", "benchmark"]
    if len(aligned) < 30:
        return np.nan, np.nan, np.nan, np.nan
    regression = linregress(aligned["benchmark"], aligned["fund"])
    alpha = regression.intercept * TRADING_DAYS
    beta = regression.slope
    active_return = aligned["fund"] - aligned["benchmark"]
    tracking_error = active_return.std() * math.sqrt(TRADING_DAYS)
    information_ratio = active_return.mean() * TRADING_DAYS / tracking_error if tracking_error else np.nan
    return alpha, beta, tracking_error, information_ratio


def percentile_score(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    rank = series.rank(pct=True, ascending=higher_is_better)
    return (rank * 100).fillna(0)


def main() -> None:
    ensure_directories()
    sns.set_theme(style="whitegrid", palette="Set2")

    fund = pd.read_csv(DATA_PROCESSED / "clean_fund_master.csv", dtype={"amfi_code": str})
    nav = pd.read_csv(DATA_PROCESSED / "clean_nav_history.csv", parse_dates=["date"], dtype={"amfi_code": str})
    benchmarks = pd.read_csv(DATA_PROCESSED / "clean_benchmarks.csv", parse_dates=["date"])

    nav["daily_return"] = nav["daily_return_pct"] / 100
    benchmarks["daily_return"] = benchmarks["daily_return_pct"] / 100
    benchmark_returns = (
        benchmarks[benchmarks["index_name"].eq("NIFTY100")]
        .set_index("date")["daily_return"]
        .sort_index()
    )

    rows = []
    for amfi_code, group in nav.groupby("amfi_code"):
        group = group.sort_values("date")
        returns = group.set_index("date")["daily_return"]
        alpha, beta, tracking_error, information_ratio = alpha_beta(returns, benchmark_returns)
        rows.append(
            {
                "amfi_code": amfi_code,
                "return_ann_pct": annualized_return(returns) * 100,
                "return_1yr_pct": cagr_from_nav(group, 1) * 100,
                "return_3yr_pct": cagr_from_nav(group, 3) * 100,
                "return_5yr_pct": cagr_from_nav(group, 5) * 100,
                "sharpe_ratio": sharpe_ratio(returns),
                "sortino_ratio": sortino_ratio(returns),
                "alpha_pct": alpha * 100 if pd.notna(alpha) else np.nan,
                "beta": beta,
                "tracking_error_pct": tracking_error * 100 if pd.notna(tracking_error) else np.nan,
                "information_ratio": information_ratio,
                "max_drawdown_pct": max_drawdown(group["nav"]) * 100,
                "std_dev_ann_pct": returns.std() * math.sqrt(TRADING_DAYS) * 100,
            }
        )

    metrics = pd.DataFrame(rows).merge(
        fund[["amfi_code", "fund_house", "scheme_name", "category", "sub_category", "plan", "expense_ratio_pct", "risk_category"]],
        on="amfi_code",
        how="left",
    )
    score = (
        0.30 * percentile_score(metrics["return_3yr_pct"], True)
        + 0.25 * percentile_score(metrics["sharpe_ratio"], True)
        + 0.20 * percentile_score(metrics["alpha_pct"], True)
        + 0.15 * percentile_score(metrics["expense_ratio_pct"], False)
        + 0.10 * percentile_score(metrics["max_drawdown_pct"], True)
    )
    metrics["fund_score"] = score.round(2)
    metrics = metrics.sort_values("fund_score", ascending=False)

    metrics.to_csv(DATA_PROCESSED / "fund_performance_metrics.csv", index=False)
    metrics.to_csv(DATA_PROCESSED / "fund_scorecard.csv", index=False)
    metrics[["amfi_code", "scheme_name", "alpha_pct", "beta", "tracking_error_pct", "information_ratio"]].to_csv(
        DATA_PROCESSED / "alpha_beta.csv", index=False
    )
    nav.to_csv(DATA_PROCESSED / "returns_computed.csv", index=False)

    top5_codes = metrics.head(5)["amfi_code"].tolist()
    nav_pivot = nav[nav["amfi_code"].isin(top5_codes)].pivot(index="date", columns="amfi_code", values="nav")
    normalized_nav = nav_pivot / nav_pivot.iloc[0] * 100
    normalized_bench = (
        benchmarks[benchmarks["index_name"].isin(["NIFTY50", "NIFTY100"])]
        .pivot(index="date", columns="index_name", values="close_value")
        .sort_index()
    )
    normalized_bench = normalized_bench / normalized_bench.iloc[0] * 100

    label_map = fund.set_index("amfi_code")["scheme_name"].str.slice(0, 28).to_dict()
    plt.figure(figsize=(13, 7))
    for code in normalized_nav.columns:
        plt.plot(normalized_nav.index, normalized_nav[code], label=label_map.get(code, code), linewidth=1.5)
    for index_name in normalized_bench.columns:
        plt.plot(normalized_bench.index, normalized_bench[index_name], label=index_name, linewidth=1.8, linestyle="--")
    plt.title("Top 5 Fund Scorecard Funds vs NIFTY50 and NIFTY100")
    plt.xlabel("Date")
    plt.ylabel("Growth of Rs. 100")
    plt.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1))
    plt.tight_layout()
    plt.savefig(CHARTS / "16_top5_funds_vs_benchmarks.png", dpi=160, bbox_inches="tight")
    plt.close()

    report = [
        "# Day 4 Fund Performance Analytics",
        "",
        f"- Metrics computed for {len(metrics)} schemes.",
        f"- Risk-free rate assumption: {RISK_FREE_RATE * 100:.1f}% annual.",
        f"- Benchmark used for alpha/beta: NIFTY100.",
        "",
        "## Top 10 Fund Scorecard",
        "",
        metrics[
            [
                "scheme_name",
                "fund_house",
                "sub_category",
                "return_3yr_pct",
                "sharpe_ratio",
                "alpha_pct",
                "beta",
                "max_drawdown_pct",
                "expense_ratio_pct",
                "fund_score",
            ]
        ]
        .head(10)
        .to_markdown(index=False, floatfmt=".2f"),
        "",
    ]
    (REPORTS / "Performance_Analytics.md").write_text("\n".join(report), encoding="utf-8")
    print("Day 4 performance analytics complete.")


if __name__ == "__main__":
    main()
