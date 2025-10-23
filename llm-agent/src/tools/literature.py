"""
Literature retrieval helpers using the Semantic Scholar API.

Functions:
- fetch_articles_structured
- fetch_articles_detailed_log

These create a directory with text metadata for all papers, and download a limited number
of open-access PDFs when available.
"""

from __future__ import annotations

from pathlib import Path
import re
import time
from typing import Tuple
import json
import requests


BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
HEADERS = {"User-Agent": "LongevityKB/1.0 (https://github.com/davidzheglov/longevity-knowledge-base)"}


def _safe_name(name: str) -> str:
    return re.sub(r"[^\w\s-]", "_", name.strip())


def fetch_articles_structured(
    query: str,
    num_pdfs: int = 5,
    max_checked: int = 300,
    delay: float = 2.5,
    output_dir: str = ".",
) -> str:
    """Structured fetch: PDFs into ./<query>/pdf, metadata TXT into ./<query>/txt. Returns base folder."""
    safe = _safe_name(query)
    base = Path(output_dir) / safe
    pdf_dir = base / "pdf"
    txt_dir = base / "txt"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)

    pdf_count = 0
    total_checked = 0
    offset = 0
    batch_size = 100

    while pdf_count < num_pdfs and total_checked < max_checked:
        limit = min(batch_size, max_checked - total_checked)
        if limit <= 0:
            break
        params = {
            "query": query,
            "offset": offset,
            "limit": limit,
            "fields": "title,authors,abstract,openAccessPdf,url,year,venue,externalIds",
        }
        try:
            resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
            if resp.status_code == 429:
                time.sleep(5)
                break
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            break

        papers = data.get("data", [])
        if not papers:
            break
        for paper in papers:
            if total_checked >= max_checked or pdf_count >= num_pdfs:
                break
            total_checked += 1
            title = (paper.get("title") or "Untitled").strip()
            abstract = paper.get("abstract") or "Abstract not available."
            publisher_url = paper.get("url", "N/A")
            oa = paper.get("openAccessPdf") or {}
            pdf_url = oa.get("url")
            authors = ", ".join([a.get("name", "") for a in (paper.get("authors") or [])][:3])
            year = paper.get("year", "N/A")
            venue = paper.get("venue", "N/A")
            ext = (paper.get("externalIds") or {})
            doi = ext.get("DOI")

            base_fn = re.sub(r"[^\w\-_.]", "_", title[:60])
            txt_path = txt_dir / f"{total_checked:03d}_{base_fn}.txt"
            txt_path.write_text(
                f"Title: {title}\nAuthors: {authors}\nYear: {year}\nVenue: {venue}\n"
                f"DOI: {doi or 'N/A'}\nPublisher URL: {publisher_url}\nOpenAccess PDF URL: {pdf_url or 'N/A'}\n\n"
                f"Abstract:\n{abstract}\n",
                encoding="utf-8",
            )

            if not pdf_url:
                continue
            try:
                pr = requests.get(pdf_url, timeout=30, stream=True, headers=HEADERS)
                if pr.status_code != 200:
                    continue
                content_type = pr.headers.get("Content-Type", "").lower()
                pdf_path = pdf_dir / f"{total_checked:03d}_{base_fn}.pdf"
                # Read in chunks and also detect PDF via first chunk
                first_chunk = b""
                with pdf_path.open("wb") as f:
                    for chunk in pr.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        if not first_chunk:
                            first_chunk = chunk[:10]
                        f.write(chunk)
                if ("application/pdf" in content_type) or (b"%PDF" in first_chunk):
                    pdf_count += 1
                else:
                    # Not a PDF; remove file
                    try: pdf_path.unlink()
                    except Exception: pass
            except Exception:
                pass
            time.sleep(0.5)
        offset += len(papers)
        time.sleep(delay)

    return str(base.resolve())


def fetch_articles_detailed_log(
    query: str,
    num_pdfs: int = 5,
    max_checked: int = 300,
    delay: float = 2.5,
    output_dir: str = ".",
) -> str:
    """Detailed logging variant: saves TXT for all; PDFs for open access; returns folder."""
    safe = _safe_name(query)
    base = Path(output_dir) / safe
    base.mkdir(parents=True, exist_ok=True)

    pdf_count = 0
    total_checked = 0
    offset = 0
    batch_size = 100

    log_path = base / "download_log.txt"
    with log_path.open("w", encoding="utf-8") as lg:
        while pdf_count < num_pdfs and total_checked < max_checked:
            limit = min(batch_size, max_checked - total_checked)
            if limit <= 0:
                break
            params = {
                "query": query,
                "offset": offset,
                "limit": limit,
                "fields": "title,authors,abstract,openAccessPdf,url,year,venue,externalIds",
            }
            try:
                resp = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=20)
                if resp.status_code == 429:
                    lg.write("Rate limited (429). Backing off.\n")
                    time.sleep(5)
                    break
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                lg.write(f"API error: {e}\n")
                break

            papers = data.get("data", [])
            if not papers:
                break
            for paper in papers:
                if total_checked >= max_checked or pdf_count >= num_pdfs:
                    break
                total_checked += 1
                title = (paper.get("title") or "Untitled").strip()[:80]
                oa = paper.get("openAccessPdf") or {}
                pdf_url = oa.get("url")
                authors = ", ".join([a.get("name", "") for a in (paper.get("authors") or [])][:3])
                ext = (paper.get("externalIds") or {})
                doi = ext.get("DOI")
                log_prefix = f"[{total_checked:03d}] {title} | Authors: {authors}"

                base_fn = re.sub(r"[^\w\-_.]", "_", title[:60])
                txt_path = base / f"{total_checked:03d}_{base_fn}.txt"
                with txt_path.open("w", encoding="utf-8") as f:
                    f.write(json.dumps(paper, ensure_ascii=False, indent=2))
                    if doi:
                        f.write(f"\n\nDOI: {doi}\n")

                if not pdf_url:
                    lg.write(f"{log_prefix} -> No open-access PDF\n")
                    continue

                try:
                    pr = requests.get(pdf_url, timeout=30, stream=True, headers=HEADERS)
                    if pr.status_code != 200:
                        lg.write(f"{log_prefix} -> PDF HTTP {pr.status_code}\n")
                        continue
                    content_type = pr.headers.get("Content-Type", "").lower()
                    pdf_path = base / f"{total_checked:03d}_{base_fn}.pdf"
                    first_chunk = b""
                    with pdf_path.open("wb") as f:
                        for chunk in pr.iter_content(chunk_size=8192):
                            if not chunk:
                                continue
                            if not first_chunk:
                                first_chunk = chunk[:10]
                            f.write(chunk)
                    if ("application/pdf" in content_type) or (b"%PDF" in first_chunk):
                        pdf_count += 1
                        lg.write(f"{log_prefix} -> PDF #{pdf_count} saved\n")
                    else:
                        try: pdf_path.unlink()
                        except Exception: pass
                        lg.write(f"{log_prefix} -> Not a PDF response\n")
                except Exception as e:
                    lg.write(f"{log_prefix} -> Error: {e}\n")
                time.sleep(0.5)
            offset += len(papers)
            time.sleep(delay)

    return str(base.resolve())
