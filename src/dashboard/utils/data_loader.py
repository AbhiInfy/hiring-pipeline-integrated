from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError


def load_summary(path: Path) -> dict:
    """Load pipeline_summary.json"""
    if not path.exists():
        return {}

    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> pd.DataFrame:
    """Safely load CSV files."""
    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


def get_output_paths():
    """
    Returns all output file paths used by the dashboard.
    """

    root = Path(__file__).resolve().parents[3]

    output_dir = root / "output"

    return {
        "output_dir": output_dir,
        "shortlist_file": output_dir / "shortlisted_profiles.csv",
        "dispatch_file": output_dir / "email_dispatch.csv",
        "summary_file": output_dir / "pipeline_summary.json",
    }