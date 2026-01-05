import csv
from pathlib import Path
from typing import Dict, Iterable, List

def ensure_path_exists(path: Path) -> None:
    """Ensure that the directory for the given path exists."""
    path.parent.mkdir(parents=True, exist_ok=True)

def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    """Read a CSV file and return a list of dictionaries."""
    rows: List[Dict[str, str]] = []
    with path.open(mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: (v or "").strip() for k, v in row.items()})
    
    return rows

def write_csv_dicts(path: Path, rows: Iterable[Dict[str, str]], fieldnames: List[str]) -> None:
    """Write a list of dictionaries to a CSV file."""
    ensure_path_exists(path)
    with path.open(mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)