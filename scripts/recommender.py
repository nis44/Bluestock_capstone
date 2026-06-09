"""Simple fund recommender for Bluestock MF capstone."""

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
        print(f"\nTop recommendations for {appetite} risk appetite")
        print(recommend_funds(appetite).to_string(index=False))
