from pathlib import Path
import logging
from tqdm import tqdm

from govscrape.config import ScrapeConfig
from govscrape.io_utils import read_csv_dicts, ensure_parent
from govscrape.http import HttpClient
from govscrape.robots import allowed_by_robots

def setup_logger(log_file: Path) -> None:
    ensure_parent(log_file)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )

def safe_filename(url: str) -> str:
    # basic filename extraction
    base = url.split("?")[0].split("#")[0].rstrip("/")
    name = base.split("/")[-1] or "download.pdf"
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name

def main():
    cfg = ScrapeConfig()
    setup_logger(cfg.log_file)

    if not cfg.discovered_csv.exists():
        raise FileNotFoundError(f"Missing {cfg.discovered_csv}. Run scrape_discover first.")

    rows = read_csv_dicts(cfg.discovered_csv)
    client = HttpClient(cfg.user_agent, cfg.timeout_sec, cfg.delay_sec)

    out_dir = cfg.out_dir / "pdfs"
    out_dir.mkdir(parents=True, exist_ok=True)

    for r in tqdm(rows, desc="Downloading PDFs"):
        url = r["url"]

        if not allowed_by_robots(url, cfg.user_agent):
            logging.warning(f"Blocked by robots.txt: {url}")
            continue

        fname = out_dir / safe_filename(url)
        if fname.exists() and fname.stat().st_size > 0:
            continue

        try:
            data = client.download_bytes(url)
            fname.write_bytes(data)
        except Exception as e:
            logging.error(f"Failed download {url}: {e}")
            continue

    logging.info(f"Downloads complete -> {out_dir}")

if __name__ == "__main__":
    main()
