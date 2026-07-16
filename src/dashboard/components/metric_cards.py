import streamlit as st

from utils.data_loader import (
    get_output_paths,
    load_summary,
)


def render_metric_cards():
    """Render dashboard KPI metric cards."""

    # Load pipeline summary
    paths = get_output_paths()
    summary = load_summary(paths["summary_file"])

    # Get values safely
    total_candidates = summary.get("total_candidates", 0)
    total_matches = summary.get("total_matches", 0)
    total_jobs = summary.get("total_jobs", 0)
    emails_sent = summary.get("emails_sent", 0)
    emails_failed = summary.get("emails_failed", 0)

    # KPI Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.metric("Candidates Found", total_candidates)

    with kpi2:
        st.metric("Matched Candidates", total_matches)

    with kpi3:
        st.metric("Jobs Found", total_jobs)

    with kpi4:
        st.metric("Emails Sent", emails_sent)

    with kpi5:
        st.metric("Email Failures", emails_failed)