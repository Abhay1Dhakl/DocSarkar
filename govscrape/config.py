from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ScrapingConfig:
    user_agent: str = "GovSearchBot/1.0 (academic; contact: abhaydhkal@gmail.com)"
    timeout_sec: int = 30
    delay_sec: float = 3.0  # be polite
    max_pages_per_seed: int = 50  # safety limit
    out_dir: Path = Path("data/raw")
    sources_csv: Path = Path("data/sources/sources.csv")
    discovered_csv: Path = Path("data/sources/discovered_links.csv")
    log_file: Path = Path("data/logs/scraper.log")