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

    requested_jd_mode = str(summary.get("requested_jd_mode", "")).strip()
    used_jd_mode = str(summary.get("used_jd_mode", "")).strip()
    requested_matching_mode = str(summary.get("requested_matching_mode", "")).strip()
    used_matching_mode = str(summary.get("used_matching_mode", "")).strip()
    warnings = summary.get("warnings", []) if isinstance(summary.get("warnings", []), list) else []

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

    if requested_jd_mode or used_jd_mode or requested_matching_mode or used_matching_mode:
        st.markdown("### Runtime Modes")
        st.write(
            {
                "requested_jd_mode": requested_jd_mode,
                "used_jd_mode": used_jd_mode,
                "requested_matching_mode": requested_matching_mode,
                "used_matching_mode": used_matching_mode,
            }
        )

    if warnings:
        st.markdown("### Pipeline Warnings")
        for warning in warnings:
            st.warning(str(warning))

    if shortlist_df.empty:
        st.info("No matches met the configured threshold.")
        return

    st.markdown("### Top Matches")
    st.dataframe(shortlist_df, use_container_width=True)

    st.markdown("### Score Distribution")

    # Determine which score column to use
    # Semantic matching uses 'final_score', token-based uses 'match_score'
    score_column = None
    if "final_score" in shortlist_df.columns:
        score_column = "final_score"
    elif "match_score" in shortlist_df.columns:
        score_column = "match_score"

    if score_column:
        st.bar_chart(
            shortlist_df.groupby("candidate_name")[score_column]
            .max()
            .sort_values(ascending=False)
            .head(20)
        )
    else:
        st.warning("No score column found in matches data")

    # Show semantic matching details if available
    if "semantic_score" in shortlist_df.columns and "token_score" in shortlist_df.columns:
        st.markdown("### Semantic Matching Details")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Avg Semantic Score",
                f"{shortlist_df['semantic_score'].mean():.3f}",
                help="Cosine similarity of embeddings (higher = more semantically similar)"
            )

        with col2:
            st.metric(
                "Avg Token Score",
                f"{shortlist_df['token_score'].mean():.3f}",
                help="Jaccard similarity of keywords (higher = more keyword overlap)"
            )

        with col3:
            st.metric(
                "Avg Final Score",
                f"{shortlist_df['final_score'].mean():.3f}",
                help="Blended score (70% semantic + 30% token)"
            )

        # Show score comparison
        st.markdown("#### Score Comparison")
        score_comparison = shortlist_df[["candidate_name", "semantic_score", "token_score", "final_score"]].head(10)
        st.dataframe(score_comparison, use_container_width=True)

    # Show skill match details if available
    if "skill_match_details" in shortlist_df.columns:
        st.markdown("### Skill Match Details")
        details_df = shortlist_df[["candidate_name", "role", "skill_match_details"]].head(20)
        st.dataframe(details_df, use_container_width=True)

    if dispatch_file.exists():
        st.markdown("### Email Dispatch")
        try:
            dispatch_df = pd.read_csv(dispatch_file)
            st.dataframe(dispatch_df, use_container_width=True)
        except EmptyDataError:
            st.info("Email dispatch log is empty.")


if __name__ == "__main__":
    main()
