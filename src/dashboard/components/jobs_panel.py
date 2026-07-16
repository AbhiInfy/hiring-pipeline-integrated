import streamlit as st
import pandas as pd

from utils.data_loader import (
    get_output_paths,
    load_csv,
)


def render_jobs_panel():
    """Render the top matching candidates."""

    paths = get_output_paths()

    df = load_csv(paths["shortlist_file"])

    st.subheader("💼 Top Matching Candidates")

    if df.empty:
        st.info("No shortlisted candidates available.")
        return

    df = df.sort_values(
        by="match_score",
        ascending=False,
    )

    display_df = df[
        [
            "candidate_name",
            "role",
            "company",
            "match_score",
        ]
    ].copy()

    display_df["match_score"] = (
        display_df["match_score"] * 100
    ).round(2).astype(str) + "%"

    display_df.columns = [
        "Candidate",
        "Role",
        "Company",
        "Match Score",
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )