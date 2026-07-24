import streamlit as st

from utils.data_loader import (
    get_output_paths,
    load_summary,
)


def _clamp_progress(value: float) -> float:
    """Return a safe Streamlit progress value in [0.0, 1.0]."""
    return max(0.0, min(1.0, value))


def render_analysis_summary():
    """Render AI analysis summary."""

    paths = get_output_paths()
    summary = load_summary(paths["summary_file"])

    matching_mode = summary.get("used_matching_mode", "Unknown")
    jd_mode = summary.get("used_jd_mode", "Unknown")
    total_candidates = summary.get("total_candidates", 0)
    total_matches = summary.get("total_matches", 0)
    emails_sent = summary.get("emails_sent", 0)
    emails_failed = summary.get("emails_failed", 0)

    # Calculate percentages
    match_rate = (
        (total_matches / total_candidates) * 100
        if total_candidates > 0
        else 0
    )

    email_total = emails_sent + emails_failed

    email_rate = (
        (emails_sent / email_total) * 100
        if email_total > 0
        else 0
    )

    st.subheader("🤖 AI Analysis Summary")

    with st.container(border=True):

        # ← Paste the new custom cards here
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(...)

        with col2:
            st.markdown(...)

        with col3:
            st.markdown(...)

        st.divider()

        # Match Rate
        st.write("### 🎯 Match Rate")
        ...

        # Email Success
        st.write("### 📧 Email Success")
        ...

        # Pipeline Status
        if emails_failed == 0:
            ...

        # ==========================
        # MATCH RATE
        # ==========================

        st.write("### 🎯 Match Rate")

        st.progress(_clamp_progress(match_rate / 100))

        st.caption(
            f"{match_rate:.1f}% ({total_matches} of {total_candidates} candidates matched)"
        )

        st.write("")

        # ==========================
        # EMAIL SUCCESS
        # ==========================

        st.write("### 📧 Email Success")

        st.progress(_clamp_progress(email_rate / 100))

        st.caption(
            f"{email_rate:.1f}% ({emails_sent} sent • {emails_failed} failed)"
        )

        st.divider()

        # ==========================
        # PIPELINE STATUS
        # ==========================

        if emails_failed == 0:
            st.success("Pipeline executed successfully.")
        else:
            st.warning(
                f"Pipeline completed with {emails_failed} failed email(s)."
            )