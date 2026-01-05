from pathlib import Path
from typing import Dict, List, Set
import logging

from govscrape.config import ScrapeConfig
from govscrape.io_utils import read_csv_dicts, write_csv_dicts, ensure_path_exists
from govscrape.http import HttpClient
from govscrape.robots import allowed_by_robots
from govscrape.extract import extract_links, split_doc_links

def setup_logger(log_file: Path) -> None:
    ensure_path_exists(log_file)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_file, encoding="utf-8"), logging.StreamHandler()],
    )

def main():
    cfg = ScrapeConfig()
    setup_logger(cfg.log_file)

    if not cfg.sources_csv.exists():
        raise FileNotFoundError(f"Missing {cfg.sources_csv}. Create it first.")

    seeds = read_csv_dicts(cfg.sources_csv)
    client = HttpClient(cfg.user_agent, cfg.timeout_sec, cfg.delay_sec)

    discovered_rows: List[Dict[str, str]] = []
    seen_urls: Set[str] = set()

    for s in seeds:
        seed_url = s["seed_url"]
        source_id = s.get("source_id", "")
        org = s.get("org", "")
        doc_type = s.get("doc_type", "")

        logging.info(f"Seed: {seed_url}")

        if not allowed_by_robots(seed_url, cfg.user_agent):
            logging.warning(f"Blocked by robots.txt: {seed_url}")
            continue

        try:
            html = client.get_text(seed_url)
        except Exception as e:
            logging.error(f"Failed to fetch seed {seed_url}: {e}")
            continue

        # Optional: save raw html
        raw_dir = cfg.out_dir / "html"
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / f"{source_id or 'seed'}_page.html").write_text(html, encoding="utf-8")

        links = extract_links(html, seed_url)
        pdf_links, html_links = split_doc_links(links)

        logging.info(f"Found {len(pdf_links)} pdf links and {len(html_links)} other links on seed page.")

        # Save discovered PDF links
        for u in pdf_links:
            if u in seen_urls:
                continue
            seen_urls.add(u)
            discovered_rows.append({
                "source_id": source_id,
                "org": org,
                "doc_type": doc_type,
                "url": u,
            })

    write_csv_dicts(
        cfg.discovered_csv,
        fieldnames=["source_id", "org", "doc_type", "url"],
        rows=discovered_rows,
    )
    logging.info(f"Wrote {len(discovered_rows)} discovered links -> {cfg.discovered_csv}")

if __name__ == "__main__":
    main()
