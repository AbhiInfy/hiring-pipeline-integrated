from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError


def _load_summary(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    st.set_page_config(page_title="Recruiter Dashboard", layout="wide")
    st.title("Recruiter Dashboard")
    st.caption("Shortlisted profiles, scores, and pipeline analytics")

    root = Path(__file__).resolve().parents[2]
    output_dir = root / "output"
    shortlist_file = output_dir / "shortlisted_profiles.csv"
    dispatch_file = output_dir / "email_dispatch.csv"
    summary_file = output_dir / "pipeline_summary.json"

    if not shortlist_file.exists():
        st.warning("No shortlisted profile data found. Run the architecture pipeline first.")
        return

    try:
        shortlist_df = pd.read_csv(shortlist_file)
    except EmptyDataError:
        shortlist_df = pd.DataFrame()
    summary = _load_summary(summary_file)

    total_jobs = int(summary.get("total_jobs", shortlist_df["row_num"].nunique() if not shortlist_df.empty else 0))
    total_candidates = int(summary.get("total_candidates", shortlist_df["candidate_name"].nunique() if not shortlist_df.empty else 0))
    total_matches = int(summary.get("total_matches", len(shortlist_df)))
    emails_sent = int(summary.get("emails_sent", 0))
    emails_failed = int(summary.get("emails_failed", 0))
    emails_dry_run = int(summary.get("emails_dry_run", 0))

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Jobs Processed", total_jobs)
    col2.metric("Candidates Considered", total_candidates)
    col3.metric("Shortlisted Matches", total_matches)
    col4.metric("Emails Sent", emails_sent)
    col5.metric("Emails Failed", emails_failed)
    col6.metric("Emails Dry Run", emails_dry_run)

    if shortlist_df.empty:
        st.info("No matches met the configured threshold.")
        return

    st.markdown("### Top Matches")
    st.dataframe(shortlist_df, use_container_width=True)

    st.markdown("### Score Distribution")
    st.bar_chart(shortlist_df.groupby("candidate_name")["match_score"].max().sort_values(ascending=False).head(20))

    if dispatch_file.exists():
        st.markdown("### Email Dispatch")
        try:
            dispatch_df = pd.read_csv(dispatch_file)
            st.dataframe(dispatch_df, use_container_width=True)
        except EmptyDataError:
            st.info("Email dispatch log is empty.")


if __name__ == "__main__":
    main()
