from __future__ import annotations

from pathlib import Path
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def _clean(value) -> str:
    """Clean and normalize string values"""
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "nat", "none", "null"}:
        return ""
    return text


def _extract_skills(skills_value) -> str:
    """
    Extract and clean skills, handling multi-line text.
    Converts newlines to commas and removes extra whitespace.
    """
    if pd.isna(skills_value):
        return ""
    
    skills_text = str(skills_value)
    # Replace newlines and carriage returns with commas
    skills_text = skills_text.replace('\n', ', ').replace('\r', ', ')
    # Replace multiple spaces with single space
    skills_text = ' '.join(skills_text.split())
    # Remove multiple commas
    while ',,' in skills_text:
        skills_text = skills_text.replace(',,', ',')
    # Remove trailing/leading commas and spaces
    skills_text = skills_text.strip(', ')
    
    return skills_text


def _validate_excel_file(path: Path) -> tuple[bool, str]:
    """
    Validate Excel file integrity before attempting to read.
    
    Returns:
        (is_valid, error_message)
    """
    if not path.exists():
        return False, f"File not found: {path}"
    
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        return False, f"Invalid format: {path.suffix}. Only .xlsx or .xls files are supported"
    
    # Check if file is empty
    if path.stat().st_size == 0:
        return False, f"File is empty (0 bytes): {path}"
    
    # Try to read file signature (first few bytes)
    try:
        with open(path, 'rb') as f:
            header = f.read(8)
            # Check for Excel file signatures
            if header[:4] == b'PK\x03\x04':  # .xlsx (ZIP format)
                pass  # Valid Excel file
            elif header[:2] == b'\xD0\xCF':  # .xls (OLE format)
                pass  # Valid Excel file
            else:
                return False, f"File does not appear to be a valid Excel file (wrong file signature)"
    except Exception as e:
        return False, f"Cannot read file header: {e}"
    
    return True, "OK"


def _ensure_seed_file(path: Path) -> bool:
    """
    Create a seed Excel file if it doesn't exist.
    
    Returns:
        True if file was created, False if it already exists
    """
    if path.exists():
        return False
    
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError(f"Candidate profiles must be stored as an Excel workbook: {path}")
    
    path.parent.mkdir(parents=True, exist_ok=True)
    seed = pd.DataFrame(
        [
            {
                "candidate_name": "Example Candidate",
                "skills": "Oracle Fusion, SQL, Python",
                "email": "candidate@example.com",
                "notice_period_days": "30",
            }
        ]
    )
    seed.to_excel(path, index=False)
    print(f"\n INFO: Created template Excel file: {path}")
    print("   Please update with your actual candidate data and re-run the pipeline")
    return True


def load_candidate_profiles(source_path: Path) -> pd.DataFrame:
    """
    Load candidate profiles from Excel file (.xlsx or .xls only).
    Handles column names with spaces, parentheses, and multi-line skills.
    
    Args:
        source_path: Path to the Excel file
        
    Returns:
        DataFrame with candidate profiles (empty if error or no valid data)
    """
    source_path = Path(source_path)
    
    # Validate file format
    if source_path.suffix.lower() not in {".xlsx", ".xls"}:
        error_msg = f"Candidate profiles must be an Excel workbook (.xlsx or .xls). Invalid file: {source_path}"
        logger.error(error_msg)
        print(f"\n{'='*60}")
        print(" ERROR: Invalid File Format")
        print(f"{'='*60}")
        print(f"File: {source_path}")
        print(f"Format: {source_path.suffix}")
        print("\nOnly Excel files (.xlsx or .xls) are supported.")
        print("Please convert your file to Excel format using Microsoft Excel or LibreOffice Calc.")
        return pd.DataFrame()
    
    # Ensure seed file exists (creates template if needed)
    try:
        is_new = _ensure_seed_file(source_path)
        if is_new:
            # Just created template, return empty DataFrame as no real data
            print("\n WARNING: Template created but no actual candidate data found.")
            print("   Please add your candidates to the Excel file and re-run.")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Failed to create seed file: {e}")
        print(f"\n ERROR: Cannot create template file: {e}")
        return pd.DataFrame()
    
    # Validate Excel file before reading
    is_valid, error_msg = _validate_excel_file(source_path)
    if not is_valid:
        logger.error(f"Excel file validation failed: {error_msg}")
        print(f"\n{'='*60}")
        print(" ERROR: Invalid Excel File")
        print(f"{'='*60}")
        print(f"File: {source_path}")
        print(f"Error: {error_msg}")
        print("\nPossible solutions:")
        print("  1. Open the file in Excel and 'Save As' a new .xlsx file")
        print("  2. Create a new Excel file with the required columns")
        print("  3. Check if the file is corrupted or open in another program")
        return pd.DataFrame()
    
    # Attempt to read the Excel file
    try:
        raw = pd.read_excel(source_path, engine='openpyxl')
        logger.info(f"Successfully loaded Excel file: {source_path}")
        print(f" Successfully loaded: {source_path.name}")
    except FileNotFoundError:
        logger.error(f"File not found after validation: {source_path}")
        print(f"\n ERROR: File not found - {source_path}")
        return pd.DataFrame()
    except PermissionError:
        logger.error(f"Permission denied: {source_path} - File may be open in Excel")
        print(f"\n{'='*60}")
        print(" ERROR: Cannot Read File - Permission Denied")
        print(f"{'='*60}")
        print(f"File: {source_path}")
        print("\nThe file may be open in another program (like Excel).")
        print("Please close the file and re-run the pipeline.")
        return pd.DataFrame()
    except ValueError as e:
        logger.error(f"Corrupted or invalid Excel file: {e}")
        print(f"\n{'='*60}")
        print("ERROR: Corrupted or Invalid Excel File")
        print(f"{'='*60}")
        print(f"File: {source_path}")
        print(f"Error: {str(e)}")
        print("\nPossible causes:")
        print("  • The file is corrupted")
        print("  • The file is not a valid Excel file")
        print("  • The file was saved in an incompatible format")
        print("\nSolutions:")
        print("  1. Open the file in Excel and 'Save As' a new .xlsx file")
        print("  2. Create a new Excel file with the required columns")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected error reading Excel file: {e}")
        print(f"\n ERROR: Failed to read Excel file: {e}")
        return pd.DataFrame()
    
    # Check if file is empty
    if raw.empty:
        logger.warning(f"Excel file is empty: {source_path}")
        print(f"\n WARNING: Excel file is empty: {source_path.name}")
        print("Please add candidate data to the file and re-run.")
        return pd.DataFrame()
    
    # Print found columns for debugging
    print(f"\n INFO: Found columns in Excel: {list(raw.columns)}")
    
    # Create a new DataFrame for mapped data
    mapped_data = {}
    
    # ========== SMART COLUMN MAPPING ==========
    # Map 'Candidate Name' (with space) to candidate_name
    if 'Candidate Name' in raw.columns:
        mapped_data['candidate_name'] = raw['Candidate Name'].apply(_clean)
        print("    Mapped 'Candidate Name' -> candidate_name")
    elif 'candidate_name' in raw.columns:
        mapped_data['candidate_name'] = raw['candidate_name'].apply(_clean)
    else:
        # Try case-insensitive search for name column
        for col in raw.columns:
            if 'name' in col.lower():
                mapped_data['candidate_name'] = raw[col].apply(_clean)
                print(f"    Mapped '{col}' -> candidate_name")
                break
    
    # Map 'Email ID' (with space) to email
    if 'Email ID' in raw.columns:
        mapped_data['email'] = raw['Email ID'].apply(_clean)
        print("    Mapped 'Email ID' -> email")
    elif 'email' in raw.columns:
        mapped_data['email'] = raw['email'].apply(_clean)
    else:
        # Try case-insensitive search for email column
        for col in raw.columns:
            if 'email' in col.lower():
                mapped_data['email'] = raw[col].apply(_clean)
                print(f"    Mapped '{col}' -> email")
                break
    
    # Map 'Skills' (with multi-line text) to skills
    if 'Skills' in raw.columns:
        mapped_data['skills'] = raw['Skills'].apply(_extract_skills)
        print("    Mapped 'Skills' -> skills (multi-line support)")
    elif 'skills' in raw.columns:
        mapped_data['skills'] = raw['skills'].apply(_extract_skills)
    else:
        # Try case-insensitive search for skills column
        for col in raw.columns:
            if 'skill' in col.lower():
                mapped_data['skills'] = raw[col].apply(_extract_skills)
                print(f"   Mapped '{col}' -> skills (multi-line support)")
                break
    
    # Map 'Notice Period (Days)' (with parentheses) to notice_period_days
    if 'Notice Period (Days)' in raw.columns:
        mapped_data['notice_period_days'] = raw['Notice Period (Days)'].apply(_clean)
        print("    Mapped 'Notice Period (Days)' -> notice_period_days")
    elif 'notice_period_days' in raw.columns:
        mapped_data['notice_period_days'] = raw['notice_period_days'].apply(_clean)
    else:
        # Try case-insensitive search for notice column
        for col in raw.columns:
            if 'notice' in col.lower():
                mapped_data['notice_period_days'] = raw[col].apply(_clean)
                print(f"  Mapped '{col}' -> notice_period_days")
                break
    
    # Create DataFrame from mapped data
    if not mapped_data:
        print("\n ERROR: No recognizable columns found in Excel file")
        print("Please ensure your file has columns like:")
        print("  • Candidate Name")
        print("  • Skills")
        print("  • Email ID")
        print("  • Notice Period (Days)")
        return pd.DataFrame()
    
    normalized = pd.DataFrame(mapped_data)
    
    # Ensure all required columns exist (add empty if missing)
    required = ["candidate_name", "skills", "email", "notice_period_days"]
    for column in required:
        if column not in normalized.columns:
            normalized[column] = ""
            print(f"   WARNING: Added missing column: {column} (empty)")
    
    # Filter out rows with empty candidate names or skills
    before_count = len(normalized)
    normalized = normalized[(normalized["candidate_name"] != "") & (normalized["skills"] != "")]
    after_count = len(normalized)
    
    if before_count != after_count:
        removed = before_count - after_count
        logger.warning(f"Removed {removed} rows with missing candidate names or skills")
        print(f" WARNING: Removed {removed} row(s) with missing candidate names or skills")
    
    # Remove duplicates
    normalized = normalized.drop_duplicates(subset=["candidate_name", "email"]).reset_index(drop=True)
    
    # Final validation
    if normalized.empty:
        print("\n ERROR: No valid candidate profiles found after processing")
        print("Please ensure your Excel file contains at least one row with:")
        print("  • Candidate Name (non-empty)")
        print("  • Skills (non-empty)")
        print("  • Email ID")
        print("  • Notice Period (Days)")
        return pd.DataFrame()
    
    # Print success summary
    print(f"\n Successfully loaded {len(normalized)} candidate profile(s)")
    print(f"   Columns: {', '.join(normalized.columns.tolist())}")
    
    # Show sample of first candidate (skills truncated)
    sample_skills = normalized.iloc[0]['skills']
    if len(sample_skills) > 80:
        sample_skills = sample_skills[:80] + "..."
    print(f"   Sample: {normalized.iloc[0]['candidate_name']} - {sample_skills}")
    
    return normalized