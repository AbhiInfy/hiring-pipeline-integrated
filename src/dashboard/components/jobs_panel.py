import streamlit as st

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

    # Jaccard output uses match_score; semantic output uses final_score.
    score_col = "final_score" if "final_score" in df.columns else "match_score"
    if score_col not in df.columns:
        st.warning("Shortlist file has no score column to display.")
        st.dataframe(df, use_container_width=True, hide_index=True)
        return

    df = df.sort_values(by=score_col, ascending=False)

    base_cols = [col for col in ["candidate_name", "role", "company"] if col in df.columns]
    score_cols = [score_col]
    for col in ["semantic_score", "token_score", "overlap_terms"]:
        if col in df.columns:
            score_cols.append(col)

    display_df = df[base_cols + score_cols].copy()

    for col in score_cols:
        if col == "overlap_terms":
            continue
        display_df[col] = (display_df[col].astype(float) * 100).round(2).astype(str) + "%"

    rename_map = {
        "candidate_name": "Candidate",
        "role": "Role",
        "company": "Company",
        "final_score": "Final Score",
        "match_score": "Match Score",
        "semantic_score": "Semantic Score",
        "token_score": "Token Score",
        "overlap_terms": "Overlap Terms",
    }
    display_df = display_df.rename(columns=rename_map)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )
