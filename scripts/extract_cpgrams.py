"""
extract_cpgrams.py

Purpose:
- Extract structured grievance data from CPGRAMS monthly PDF reports
- Focus on:
  1. Department of Food and Public Distribution metrics (PDS-relevant)
  2. Overall ministry grievance statistics
  3. State-wise metrics where available
- Generate clean CSVs for PGSM analysis

Run:
source ~/Projects/venv/bin/activate && cd ~/Projects/civinigrani
python scripts/extract_cpgrams.py
"""

import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

import pdfplumber
import pandas as pd

# ---------------------------
# Config
# ---------------------------
ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cpgrams_extractor")

# Keywords to identify PDS-related departments
PDS_KEYWORDS = [
    "food and public distribution",
    "consumer affairs",
    "food",
    "pds",
]

# ---------------------------
# PDF Date Extraction
# ---------------------------

def extract_report_date(pdf_path: Path) -> Optional[str]:
    """
    Extract the report month/year from the PDF filename or content.
    Expected filename format: DD-MM-YYYY.pdf or similar
    Returns: YYYY-MM string
    """
    # Try from filename first
    fname = pdf_path.stem
    
    # Pattern: DD-MM-YYYY
    match = re.match(r"(\d{2})-(\d{2})-(\d{4})", fname)
    if match:
        day, month, year = match.groups()
        return f"{year}-{month}"
    
    # Try to extract from first page text
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.pages:
                text = pdf.pages[0].extract_text() or ""
                # Look for "December, 2025" or "December 2025" pattern
                month_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)[,\s]+(\d{4})"
                m = re.search(month_pattern, text, re.IGNORECASE)
                if m:
                    month_name, year = m.groups()
                    month_num = datetime.strptime(month_name, "%B").month
                    return f"{year}-{month_num:02d}"
    except Exception as e:
        logger.warning(f"Could not extract date from PDF content: {e}")
    
    return None


# ---------------------------
# Ministry Grievance Extraction
# ---------------------------

def extract_ministry_grievances(pdf_path: Path) -> pd.DataFrame:
    """
    Extract ministry-wise grievance statistics from CPGRAMS PDF.
    Looks for tables with columns like: Ministry/Department, Brought Forward, Receipts, Disposal, Pending
    """
    results = []
    report_date = extract_report_date(pdf_path)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if not tables:
                    continue
                
                for table in tables:
                    if not table or len(table) < 3:
                        continue
                    
                    # Try to find grievance data tables
                    # Look for header row containing key terms
                    header_row = None
                    for i, row in enumerate(table[:5]):  # Check first 5 rows for header
                        row_text = " ".join(str(c or "").lower() for c in row)
                        if any(kw in row_text for kw in ["ministry", "department", "receipts", "disposal", "pending"]):
                            header_row = i
                            break
                    
                    if header_row is None:
                        continue
                    
                    # Parse data rows
                    for row in table[header_row + 1:]:
                        if not row or len(row) < 4:
                            continue
                        
                        # Extract ministry/department name (usually first non-empty cell)
                        ministry = None
                        for cell in row[:4]:
                            if cell and str(cell).strip() and not str(cell).strip().isdigit():
                                ministry = str(cell).strip().replace("\n", " ")
                                break
                        
                        if not ministry:
                            continue
                        
                        # Try to extract numeric values (Receipts, Disposal, Pending)
                        numbers = []
                        for cell in row:
                            if cell:
                                # Extract numbers from cell
                                nums = re.findall(r"[\d,]+", str(cell))
                                for n in nums:
                                    try:
                                        numbers.append(int(n.replace(",", "")))
                                    except ValueError:
                                        pass
                        
                        # We need at least 3 numbers (receipts, disposal, pending)
                        if len(numbers) >= 3:
                            # Check if this is PDS-related
                            is_pds = any(kw in ministry.lower() for kw in PDS_KEYWORDS)
                            
                            results.append({
                                "report_date": report_date,
                                "ministry_department": ministry,
                                "is_pds_related": is_pds,
                                "brought_forward": numbers[0] if len(numbers) > 3 else None,
                                "receipts": numbers[-3] if len(numbers) >= 3 else numbers[0],
                                "disposal": numbers[-2] if len(numbers) >= 3 else numbers[1],
                                "pending": numbers[-1],
                                "source_page": page_num,
                                "source_file": pdf_path.name,
                            })
    
    except Exception as e:
        logger.error(f"Error extracting ministry grievances from {pdf_path}: {e}")
    
    return pd.DataFrame(results)


# ---------------------------
# PDS Department Focus Extraction
# ---------------------------

def extract_pds_metrics(pdf_path: Path) -> pd.DataFrame:
    """
    Extract specific metrics for Department of Food and Public Distribution.
    Also extracts GRAI score if available.
    """
    results = []
    report_date = extract_report_date(pdf_path)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text() or ""
                full_text += text + "\n"
            
            # Search for PDS department mentions
            pds_patterns = [
                r"Department of Food and Public Distribution[^\n]*?(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
                r"Food and Public Distribution[^\n]*?(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)",
            ]
            
            for pattern in pds_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                for m in matches:
                    nums = [int(n.replace(",", "")) for n in m]
                    results.append({
                        "report_date": report_date,
                        "ministry_department": "Department of Food and Public Distribution",
                        "metric_type": "grievance_count",
                        "brought_forward": nums[0] if len(nums) > 3 else None,
                        "receipts": nums[-3] if len(nums) >= 3 else nums[0],
                        "disposal": nums[-2] if len(nums) >= 3 else nums[1],
                        "pending": nums[-1],
                        "source_file": pdf_path.name,
                    })
                    break  # Take first match only
                if results:
                    break
    
    except Exception as e:
        logger.error(f"Error extracting PDS metrics: {e}")
    
    return pd.DataFrame(results)


# ---------------------------
# State-wise Extraction (UP focus)
# ---------------------------

def extract_up_mentions(pdf_path: Path) -> pd.DataFrame:
    """
    Extract any Uttar Pradesh specific mentions from the PDF.
    """
    results = []
    report_date = extract_report_date(pdf_path)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                
                # Look for UP mentions with numbers
                up_patterns = [
                    r"Uttar Pradesh[^\n]*?(\d[\d,]+)",
                    r"(\d[\d,]+)[^\n]*Uttar Pradesh",
                ]
                
                for pattern in up_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for m in matches:
                        num = int(m.replace(",", ""))
                        # Context extraction
                        context_match = re.search(
                            rf".{{0,100}}Uttar Pradesh.{{0,100}}",
                            text, re.IGNORECASE
                        )
                        context = context_match.group(0).strip() if context_match else ""
                        
                        results.append({
                            "report_date": report_date,
                            "state": "Uttar Pradesh",
                            "value": num,
                            "context": context[:200],
                            "source_page": page_num,
                            "source_file": pdf_path.name,
                        })
    
    except Exception as e:
        logger.error(f"Error extracting UP mentions: {e}")
    
    return pd.DataFrame(results)


# ---------------------------
# Aggregated PGSM Output
# ---------------------------

def create_pgsm_output(ministry_df: pd.DataFrame, pds_df: pd.DataFrame, up_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create the final PGSM-compatible output with month and grievance_signals columns.
    """
    records = []
    
    # From ministry data - filter PDS-related
    if not ministry_df.empty:
        pds_rows = ministry_df[ministry_df["is_pds_related"] == True]
        for _, row in pds_rows.iterrows():
            records.append({
                "month": row.get("report_date"),
                "grievance_signals": row.get("receipts", 0) + row.get("pending", 0),
                "source": "ministry_grievance",
                "ministry": row.get("ministry_department"),
                "receipts": row.get("receipts"),
                "disposal": row.get("disposal"),
                "pending": row.get("pending"),
            })
    
    # From PDS-specific metrics
    if not pds_df.empty:
        for _, row in pds_df.iterrows():
            records.append({
                "month": row.get("report_date"),
                "grievance_signals": row.get("receipts", 0) + row.get("pending", 0),
                "source": "pds_direct",
                "ministry": row.get("ministry_department"),
                "receipts": row.get("receipts"),
                "disposal": row.get("disposal"),
                "pending": row.get("pending"),
            })
    
    # From UP mentions
    if not up_df.empty:
        for _, row in up_df.iterrows():
            records.append({
                "month": row.get("report_date"),
                "grievance_signals": row.get("value", 0),
                "source": "up_mention",
                "context": row.get("context"),
            })
    
    return pd.DataFrame(records)


# ---------------------------
# Main
# ---------------------------

def main():
    logger.info("Starting CPGRAMS data extraction")
    
    # Find all CPGRAMS PDFs
    cpgrams_pdfs = list(RAW_DIR.glob("*.pdf"))
    # Filter for likely CPGRAMS reports (date-named files)
    cpgrams_pdfs = [p for p in cpgrams_pdfs if re.match(r"\d{2}-\d{2}-\d{4}", p.stem)]
    
    if not cpgrams_pdfs:
        logger.warning("No CPGRAMS PDF files found in data/raw/")
        return
    
    logger.info(f"Found {len(cpgrams_pdfs)} CPGRAMS PDF(s)")
    
    all_ministry = []
    all_pds = []
    all_up = []
    
    for pdf_path in cpgrams_pdfs:
        logger.info(f"Processing: {pdf_path.name}")
        
        # Extract different data types
        ministry_df = extract_ministry_grievances(pdf_path)
        if not ministry_df.empty:
            all_ministry.append(ministry_df)
            logger.info(f"  Extracted {len(ministry_df)} ministry grievance records")
        
        pds_df = extract_pds_metrics(pdf_path)
        if not pds_df.empty:
            all_pds.append(pds_df)
            logger.info(f"  Extracted {len(pds_df)} PDS-specific records")
        
        up_df = extract_up_mentions(pdf_path)
        if not up_df.empty:
            all_up.append(up_df)
            logger.info(f"  Extracted {len(up_df)} UP mention records")
    
    # Combine all data
    ministry_combined = pd.concat(all_ministry, ignore_index=True) if all_ministry else pd.DataFrame()
    pds_combined = pd.concat(all_pds, ignore_index=True) if all_pds else pd.DataFrame()
    up_combined = pd.concat(all_up, ignore_index=True) if all_up else pd.DataFrame()
    
    # Save individual extracts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not ministry_combined.empty:
        out_path = PROCESSED_DIR / f"cpgrams_ministry_grievances_{timestamp}.csv"
        ministry_combined.to_csv(out_path, index=False)
        logger.info(f"Saved ministry grievances to {out_path}")
    
    if not pds_combined.empty:
        out_path = PROCESSED_DIR / f"cpgrams_pds_metrics_{timestamp}.csv"
        pds_combined.to_csv(out_path, index=False)
        logger.info(f"Saved PDS metrics to {out_path}")
    
    if not up_combined.empty:
        out_path = PROCESSED_DIR / f"cpgrams_up_mentions_{timestamp}.csv"
        up_combined.to_csv(out_path, index=False)
        logger.info(f"Saved UP mentions to {out_path}")
    
    # Create PGSM-compatible output
    pgsm_df = create_pgsm_output(ministry_combined, pds_combined, up_combined)
    if not pgsm_df.empty:
        out_path = PROCESSED_DIR / f"pgsm_grievance_signals_{timestamp}.csv"
        pgsm_df.to_csv(out_path, index=False)
        logger.info(f"Saved PGSM grievance signals to {out_path}")
        print(f"\n✅ Created PGSM-compatible output: {out_path}")
        print(pgsm_df.head(10))
    else:
        logger.warning("No PGSM-compatible data extracted")
    
    logger.info("Extraction complete!")


if __name__ == "__main__":
    main()
