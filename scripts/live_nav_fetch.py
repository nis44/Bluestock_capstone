"""Day 1: fetch live historical NAV data from mfapi.in for selected schemes."""

from __future__ import annotations

import time
from typing import Iterable

import pandas as pd
import requests

from project_paths import DATA_RAW, ensure_directories


SCHEMES = {
    "hdfc_top_100": "125497",
    "sbi_bluechip": "119551",
    "icici_bluechip": "120503",
    "nippon_large_cap": "118632",
    "axis_bluechip": "119092",
    "kotak_bluechip": "120841",
}


def fetch_scheme_nav(scheme_code: str) -> pd.DataFrame:
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    rows = payload.get("data", [])
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["amfi_code", "date", "nav"])
    df["amfi_code"] = scheme_code
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna(subset=["date", "nav"]).sort_values("date")
    return df[["amfi_code", "date", "nav"]]


def fetch_all(schemes: dict[str, str]) -> Iterable[tuple[str, pd.DataFrame]]:
    for slug, code in schemes.items():
        yield slug, fetch_scheme_nav(code)
        time.sleep(0.5)


def main() -> None:
    ensure_directories()
    output_dir = DATA_RAW / "live_nav"
    output_dir.mkdir(parents=True, exist_ok=True)
    for slug, df in fetch_all(SCHEMES):
        output_file = output_dir / f"{slug}_nav.csv"
        df.to_csv(output_file, index=False)
        print(f"Saved {len(df):,} rows: {output_file}")


if __name__ == "__main__":
    main()
