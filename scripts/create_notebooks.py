"""Create lightweight notebook deliverables that run the project scripts."""

from __future__ import annotations

import nbformat as nbf

from project_paths import ROOT, ensure_directories


def make_notebook(title: str, overview: str, commands: list[str]):
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        nbf.v4.new_markdown_cell(f"# {title}\n\n{overview}"),
        nbf.v4.new_markdown_cell("## Run From Project Root"),
    ]
    for command in commands:
        nb["cells"].append(nbf.v4.new_code_cell(command))
    return nb


def main() -> None:
    ensure_directories()
    notebooks = {
        "01_data_ingestion.ipynb": make_notebook(
            "Day 1 Data Ingestion",
            "Profiles the 10 raw Bluestock datasets, validates AMFI codes, and fetches live NAV files.",
            [
                "%run ../scripts/data_ingestion.py",
                "%run ../scripts/live_nav_fetch.py",
            ],
        ),
        "02_data_cleaning_sql.ipynb": make_notebook(
            "Day 2 Data Cleaning and SQL Load",
            "Cleans raw datasets, writes processed CSVs, rebuilds SQLite tables, and exports SQL query results.",
            [
                "%run ../scripts/clean_and_load.py",
            ],
        ),
        "03_eda_analysis.ipynb": make_notebook(
            "Day 3 Exploratory Data Analysis",
            "Generates EDA charts and writes the computed findings summary.",
            [
                "%run ../scripts/eda_analysis.py",
            ],
        ),
    }
    output_dir = ROOT / "notebooks"
    output_dir.mkdir(exist_ok=True)
    for filename, notebook in notebooks.items():
        nbf.write(notebook, output_dir / filename)
        print(f"Created {output_dir / filename}")


if __name__ == "__main__":
    main()
