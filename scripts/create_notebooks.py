"""Create notebook deliverables with the project scripts embedded as code cells."""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf

from project_paths import ROOT, ensure_directories


def split_code_into_cells(source: str, max_lines: int = 90) -> list[str]:
    lines = source.splitlines()
    cells: list[str] = []
    current: list[str] = []
    for line in lines:
        starts_section = line.startswith("def ") or line.startswith("class ") or line.startswith("if __name__")
        if current and starts_section and len(current) >= 25:
            cells.append("\n".join(current).strip())
            current = []
        current.append(line)
        if len(current) >= max_lines:
            cells.append("\n".join(current).strip())
            current = []
    if current:
        cells.append("\n".join(current).strip())
    return [cell for cell in cells if cell]


def make_notebook(title: str, overview: str, script_names: list[str]):
    nb = nbf.v4.new_notebook()
    nb["cells"] = [
        nbf.v4.new_markdown_cell(f"# {title}\n\n{overview}"),
        nbf.v4.new_markdown_cell(
            "The implementation below is embedded from the project scripts so the notebook can be reviewed directly. "
            "Run from the project root or keep the notebook in the `notebooks/` folder."
        ),
        nbf.v4.new_code_cell(
            "import sys\n"
            "from pathlib import Path\n\n"
            "PROJECT_ROOT = Path.cwd()\n"
            "if PROJECT_ROOT.name == 'notebooks':\n"
            "    PROJECT_ROOT = PROJECT_ROOT.parent\n"
            "if str(PROJECT_ROOT) not in sys.path:\n"
            "    sys.path.insert(0, str(PROJECT_ROOT))\n"
            "print(f'Project root: {PROJECT_ROOT}')"
        ),
    ]
    for script_name in script_names:
        path = ROOT / "scripts" / script_name
        nb["cells"].append(nbf.v4.new_markdown_cell(f"## `{script_name}`"))
        source = path.read_text(encoding="utf-8")
        source = source.replace("from project_paths import", "from scripts.project_paths import")
        for cell_source in split_code_into_cells(source):
            nb["cells"].append(nbf.v4.new_code_cell(cell_source))
    return nb


def main() -> None:
    ensure_directories()
    notebooks = {
        "01_data_ingestion.ipynb": make_notebook(
            "Day 1 Data Ingestion",
            "Profiles the 10 raw Bluestock datasets, validates AMFI codes, and fetches live NAV files.",
            [
                "data_ingestion.py",
                "live_nav_fetch.py",
            ],
        ),
        "02_data_cleaning_sql.ipynb": make_notebook(
            "Day 2 Data Cleaning and SQL Load",
            "Cleans raw datasets, writes processed CSVs, rebuilds SQLite tables, and exports SQL query results.",
            [
                "clean_and_load.py",
            ],
        ),
        "03_eda_analysis.ipynb": make_notebook(
            "Day 3 Exploratory Data Analysis",
            "Generates EDA charts and writes the computed findings summary.",
            [
                "eda_analysis.py",
            ],
        ),
        "04_performance_analytics.ipynb": make_notebook(
            "Day 4 Fund Performance Analytics",
            "Computes CAGR, Sharpe, Sortino, alpha, beta, tracking error, drawdown, and scorecard outputs.",
            [
                "compute_metrics.py",
            ],
        ),
        "05_dashboard_preparation.ipynb": make_notebook(
            "Day 5 Dashboard Preparation",
            "Exports dashboard-ready CSV files and writes the Power BI build guide.",
            [
                "prepare_dashboard.py",
            ],
        ),
        "06_advanced_analytics.ipynb": make_notebook(
            "Day 6 Advanced Analytics",
            "Computes VaR/CVaR, rolling Sharpe, cohorts, SIP continuity, sector HHI, and recommendation logic.",
            [
                "advanced_analytics.py",
                "recommender.py",
            ],
        ),
        "07_final_assets.ipynb": make_notebook(
            "Day 7 Final Assets",
            "Generates the final PDF report, PowerPoint presentation, and submission checklist.",
            [
                "generate_final_assets.py",
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
