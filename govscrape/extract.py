from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Tuple

def extract_links(html: str, base_url: str) -> List[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.select("a[href]"):
        href = a.get("href", "").strip()
        if not href:
            continue
        full = urljoin(base_url, href)
        links.append(full)
    # de-dup while preserving order
    seen = set()
    out = []
    for u in links:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out

def split_doc_links(links: List[str]) -> Tuple[List[str], List[str]]:
    """
    Returns (pdf_links, html_links) based on file extension heuristics.
    """
    pdfs = []
    htmls = []
    for u in links:
        low = u.lower().split("?")[0].split("#")[0]
        if low.endswith(".pdf"):
            pdfs.append(u)
        else:
            htmls.append(u)
    return pdfs, htmls
