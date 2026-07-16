import streamlit as st

from utils.data_loader import (
    get_output_paths,
    load_summary,
)


def render_pipeline_overview():
    """Render the pipeline overview section."""

    paths = get_output_paths()
    summary = load_summary(paths["summary_file"])

    total_jobs = summary.get("total_jobs", 0)
    total_candidates = summary.get("total_candidates", 0)
    total_matches = summary.get("total_matches", 0)
    emails_sent = summary.get("emails_sent", 0)
    emails_failed = summary.get("emails_failed", 0)

    st.subheader("📊 Pipeline Overview")

    st.container(border=True)

    with st.container(border=True):

        st.write(f"📌 **Jobs Processed:** {total_jobs}")
        st.write(f"👥 **Candidates Processed:** {total_candidates}")
        st.write(f"🎯 **Successful Matches:** {total_matches}")
        st.write(f"📧 **Emails Sent:** {emails_sent}")
        st.write(f"❌ **Failed Emails:** {emails_failed}")

        st.divider()

        if emails_failed == 0:
            st.success("Pipeline completed successfully.")
        else:
            st.warning(
                f"Pipeline completed with {emails_failed} failed email(s)."
            )