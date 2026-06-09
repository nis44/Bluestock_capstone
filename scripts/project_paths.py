from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
DATA_DB = ROOT / "data" / "db"
REPORTS = ROOT / "reports"
CHARTS = REPORTS / "charts"
SQL_DIR = ROOT / "sql"


def ensure_directories() -> None:
    for path in [DATA_RAW, DATA_PROCESSED, DATA_DB, REPORTS, CHARTS, SQL_DIR]:
        path.mkdir(parents=True, exist_ok=True)
