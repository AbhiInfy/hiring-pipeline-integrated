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

    # Sort candidates by Final AI Score
    df = df.sort_values(
        by="final_score",
        ascending=False,
    )

    # Select columns to display
    display_df = df[
        [
            "candidate_name",
            "role",
            "company",
            "final_score",
            "semantic_score",
            "token_score",
        ]
    ].copy()

    # Convert scores into percentages
    for col in ["final_score", "semantic_score", "token_score"]:
        display_df[col] = (
            display_df[col] * 100
        ).round(2).astype(str) + "%"

    # Rename columns
    display_df.columns = [
        "Candidate",
        "Role",
        "Company",
        "Final Score",
        "Semantic Score",
        "Token Score",
    ]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )