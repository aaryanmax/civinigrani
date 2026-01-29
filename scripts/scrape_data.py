"""
scrape_data.py

Purpose:
- Download PDS district CSV (official/OGD copy)
- Crawl DARPG/CPGRAMS monthly report archive and download PDFs
- Extract tables & text from PDFs (attempt) and save CSVs
- Save raw files to data/raw/ and processed outputs to data/processed/

Run:
source ~/Projects/venv/bin/activate && cd ~/Projects/civinigrani
python scripts/scrape_data.py
"""

import os
import re
import time
import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import pdfplumber
import pandas as pd
from tqdm import tqdm
from datetime import datetime

# ---------------------------
# Config / URLs you want
# ---------------------------
# Primary PDS dataset (district monthly)
PDS_CSV_URL = "https://ckandev.indiadataportal.com/dataset/f00b1bbb-7483-4607-b566-7f5d5a1527f4/resource/45ad7278-f4b1-4472-9351-1f7caf147ee0/download/pds-district-wise-monthly-wheat-and-rice.csv"

# DARPG CPGRAMS monthly report archive (list of monthly PDF links)
DARPG_ARCHIVE_URL = "https://darpg.gov.in/node/6003/"

# CPGRAMS portal (for reference)
CPGRAMS_PORTAL = "https://www.pgportal.gov.in/"

# Optional: additional search pages (data.gov.in keywords) - not auto-scraped here
DATA_GOV_SEARCH = "https://www.data.gov.in/keywords/nfsa"

# ---------------------------
# Paths
# ---------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
SAMPLES_DIR = ROOT / "data" / "samples"

# Create directories if not present
for d in (RAW_DIR, PROCESSED_DIR, SAMPLES_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------
# Logging
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("civinigrani_scraper")

HEADERS = {
    "User-Agent": "CiviNigraniScraper/1.0 (+https://example.com) - for research/demo purposes"
}

# ---------------------------
# Utilities
# ---------------------------

def download_file(url: str, dest: Path, chunk_size: int = 1024):
    """Download file with streaming and error handling."""
    try:
        logger.info(f"Downloading: {url}")
        resp = requests.get(url, headers=HEADERS, stream=True, timeout=30)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with open(dest, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc=dest.name
        ) as pbar:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
        logger.info(f"Saved: {dest}")
        return dest
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return None


def safe_get_soup(url: str):
    """Return BeautifulSoup for a URL or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logger.error(f"Failed to fetch page {url}: {e}")
        return None

# ---------------------------
# Step 1: Download PDS CSV
# ---------------------------

def fetch_pds_csv():
    out = RAW_DIR / "pds_district_monthly_wheat_rice.csv"
    if out.exists():
        logger.info(f"PDS CSV already exists at {out} - skipping download")
        return out
    res = download_file(PDS_CSV_URL, out)
    return res

# ---------------------------
# Step 2: Crawl DARPG archive and download PDFs
# ---------------------------

def find_pdf_links_from_darpg(archive_url: str):
    """
    Crawl the DARPG archive page and find PDF links.
    Returns list of absolute PDF URLs.
    """
    soup = safe_get_soup(archive_url)
    if not soup:
        return []
    links = []
    # find all <a> tags with href ending in .pdf
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            link = urljoin(archive_url, href)
            links.append(link)
    # deduplicate preserving order
    seen = set()
    unique_links = []
    for l in links:
        if l not in seen:
            unique_links.append(l)
            seen.add(l)
    logger.info(f"Found {len(unique_links)} PDF links on archive page.")
    return unique_links

def download_darpg_pdfs(max_files: int = 20):
    """
    Download PDFs discovered on DARPG archive.
    Limits to max_files (for speed during hackathon).
    """
    pdf_urls = find_pdf_links_from_darpg(DARPG_ARCHIVE_URL)
    saved = []
    for url in pdf_urls[:max_files]:
        fname = urlparse(url).path.split("/")[-1]
        # fallback name with timestamp if empty
        if not fname:
            fname = f"darpg_report_{int(time.time())}.pdf"
        dest = RAW_DIR / fname
        if dest.exists():
            logger.info(f"PDF already exists: {dest.name}, skipping")
            saved.append(dest)
            continue
        res = download_file(url, dest)
        if res:
            saved.append(res)
        # be polite
        time.sleep(1.0)
    logger.info(f"Downloaded {len(saved)} DARPG PDFs to {RAW_DIR}")
    return saved

# ---------------------------
# Step 3: Extract tables/text from PDFs
# ---------------------------

def extract_tables_from_pdf(pdf_path: Path, output_prefix: str = None):
    """
    Use pdfplumber to extract tables and write CSVs.
    Returns list of output CSV paths.
    """
    outputs = []
    try:
        logger.info(f"Opening PDF for extraction: {pdf_path}")
        with pdfplumber.open(pdf_path) as pdf:
            # iterate pages and attempt to extract tables
            page_no = 0
            for page in pdf.pages:
                page_no += 1
                try:
                    tables = page.extract_tables()
                except Exception as e:
                    logger.warning(f"Failed to extract tables on page {page_no}: {e}")
                    tables = None
                if not tables:
                    continue
                # each table is a list of rows (list of lists)
                tbl_i = 0
                for table in tables:
                    tbl_i += 1
                    # convert to DataFrame carefully
                    try:
                        df = pd.DataFrame(table)
                        # first row often header; try to detect header if not nulls
                        # simple heuristic: if many non-empty in first row and unique
                        header = df.iloc[0].astype(str).str.strip().tolist()
                        df = df[1:]
                        df.columns = header
                    except Exception:
                        # fallback - write raw
                        df = pd.DataFrame(table)
                    # basic cleaning: drop all-null columns
                    df = df.dropna(axis=1, how="all")
                    if df.shape[1] == 0 or df.shape[0] == 0:
                        continue
                    # sanitize output name
                    base = output_prefix or pdf_path.stem
                    out_name = f"{base}_p{page_no}_t{tbl_i}.csv"
                    out_path = PROCESSED_DIR / out_name
                    df.to_csv(out_path, index=False)
                    outputs.append(out_path)
                    logger.info(f"Extracted table saved to {out_path}")
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}")
    return outputs

def extract_all_pdfs(pdf_paths):
    """
    Extract tables from a list of PDFs. Return mapping pdf -> [csvs].
    """
    mapping = {}
    for p in pdf_paths:
        mapping[str(p)] = extract_tables_from_pdf(p)
    return mapping

# ---------------------------
# Step 4: Attempt to find UP rows in extracted CSVs
# ---------------------------

def filter_for_up_from_processed_csvs():
    """
    Look through processed CSVs and find rows referencing 'Uttar Pradesh' or 'UP'.
    Save filtered outputs to processed/up_extracts_<timestamp>.csv
    """
    candidate_files = list(PROCESSED_DIR.glob("*.csv"))
    matches = []
    for f in candidate_files:
        try:
            df = pd.read_csv(f, dtype=str, low_memory=False)
            # create a unified string of all values per row and search for UP
            mask = df.apply(lambda row: row.astype(str).str.contains("Uttar", case=False, na=False).any(), axis=1)
            if mask.any():
                matched = df[mask]
                matched["source_file"] = f.name
                matches.append(matched)
                logger.info(f"Found UP-related rows in {f.name} (count: {len(matched)})")
        except Exception as e:
            logger.warning(f"Could not read {f}: {e}")
    if matches:
        out = PROCESSED_DIR / f"up_aggregated_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        pd.concat(matches, ignore_index=True).to_csv(out, index=False)
        logger.info(f"Saved aggregated UP matches to {out}")
        return out
    else:
        logger.info("No UP matches found in processed CSVs.")
        return None

# ---------------------------
# Main orchestrator
# ---------------------------

def main():
    logger.info("Starting CiviNigrani data scraper")

    # Step A: download PDS CSV
    pds = fetch_pds_csv()
    if pds:
        logger.info(f"PDS CSV ready at: {pds}")

    # Step B: download DARPG PDFs (limit to recent 12 for speed)
    pdfs = download_darpg_pdfs(max_files=12)

    # Step C: extract tables from PDFs
    if pdfs:
        mapping = extract_all_pdfs(pdfs)
        logger.info("Extraction mapping complete.")

    # Step D: attempt to find UP rows/sections in processed CSVs
    up_matches = filter_for_up_from_processed_csvs()
    if up_matches:
        logger.info(f"UP matches aggregated at {up_matches}")
    else:
        logger.info("No direct UP rows found; consider manual inspection of processed files.")

    logger.info("Scrape run completed. Check data/raw and data/processed folders.")

if __name__ == "__main__":
    main()
