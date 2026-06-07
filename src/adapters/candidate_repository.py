from __future__ import annotations

from pathlib import Path

import pandas as pd


def _pick_existing_file(primary: Path, fallback: Path) -> Path:
    if primary.exists():
        return primary
    raise FileNotFoundError(f"Candidate profile workbook not found: {primary}")


def _clean(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "nat", "none", "null"}:
        return ""
    return text


def load_candidate_profiles(job_generator_dir: Path) -> pd.DataFrame:
    xlsx = job_generator_dir / "app" / "resource" / "Resource Details Sample.xlsx"
    source = _pick_existing_file(xlsx, xlsx)
    raw = pd.read_excel(source)

    renamed = raw.rename(
        columns={
            "Candidate Name": "candidate_name",
            "Skill": "skills",
            "Email ID": "email",
            "Notice Period (Days)": "notice_period_days",
        }
    )

    required = ["candidate_name", "skills", "email", "notice_period_days"]
    for column in required:
        if column not in renamed.columns:
            renamed[column] = ""

    normalized = renamed[required].copy()
    for column in required:
        normalized[column] = normalized[column].apply(_clean)

    normalized = normalized[(normalized["candidate_name"] != "") & (normalized["skills"] != "")]
    normalized = normalized.drop_duplicates(subset=["candidate_name", "skills", "email"]).reset_index(drop=True)
    return normalized
