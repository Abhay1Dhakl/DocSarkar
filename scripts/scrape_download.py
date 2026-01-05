from pathlib import Path
import hashlib
import logging
import re
from urllib.parse import urlparse
from tqdm import tqdm

from govscrape.config import ScrapeConfig
from govscrape.io_utils import read_csv_dicts, ensure_path_exists
from govscrape.http import HttpClient
from govscrape.robots import allowed_by_robots

def setup_logger(log_file: Path) -> None:
    ensure_path_exists(log_file)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )

def safe_filename(url: str, max_len: int = 120) -> str:
    # Keep filenames short and ASCII-only to avoid OS limits.
    parsed = urlparse(url)
    name = (parsed.path.rstrip("/").split("/")[-1] or "download.pdf")
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    if len(name) <= max_len:
        return name
    ext = ".pdf" if name.lower().endswith(".pdf") else ""
    stem = name[:-len(ext)] if ext else name
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    keep = max_len - len(ext) - len(digest) - 1
    if keep < 1:
        return f"{digest}{ext}"
    return f"{stem[:keep]}-{digest}{ext}"

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
