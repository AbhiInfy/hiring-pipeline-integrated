from __future__ import annotations

from pathlib import Path

import pandas as pd


def _clean(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in {"", "nan", "nat", "none", "null"}:
        return ""
    return text


def _ensure_seed_file(path: Path) -> None:
    if path.exists():
        return
    if path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError(f"Candidate profiles must be stored as an Excel workbook: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    seed = pd.DataFrame(
        [
            {
                "candidate_name": "",
                "skills": "",
                "email": "",
                "notice_period_days": "",
            }
        ]
    )
    seed.to_excel(path, index=False)


def load_candidate_profiles(source_path: Path) -> pd.DataFrame:
    source_path = Path(source_path)
    if source_path.suffix.lower() not in {".xlsx", ".xls"}:
        raise ValueError(f"Candidate profiles must be an Excel workbook: {source_path}")
    _ensure_seed_file(source_path)

    raw = pd.read_excel(source_path)

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
