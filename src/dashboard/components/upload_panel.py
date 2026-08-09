import streamlit as st

from candidate_workflow.resume_parser import extract_resume_text
from candidate_workflow.information_extractor import (
    extract_candidate_information,
)
from candidate_workflow.candidate_query_builder import (
    build_candidate_query,
)
from candidate_workflow.resume_analysis import (
    analyze_resume,
    display_resume_analysis,
)


def render_upload_panel():
    """Render the resume upload and analysis section."""

    st.subheader("📄 Upload & Analyze Resume")
    st.caption("Upload a resume file and let AI analyze it.")

    # ==========================================================
    # Session State Initialization
    # ==========================================================
    if "candidate_information" not in st.session_state:
        st.session_state.candidate_information = None

    if "search_query" not in st.session_state:
        st.session_state.search_query = ""

    if "analysis_result" not in st.session_state:
        st.session_state.analysis_result = None

    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""

    uploaded_file = st.file_uploader(
        "Choose a Resume",
        type=["pdf", "docx"],
        help="Supported formats: PDF and DOCX",
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        analyze = st.button(
            "🔍 Analyze",
            use_container_width=True,
            disabled=uploaded_file is None,
        )

    with col2:
        if uploaded_file:
            st.success(f"Uploaded: {uploaded_file.name}")
        else:
            st.info("Please upload a resume to begin analysis.")

    find_jobs = False

    # ==========================================================
    # Run Analysis
    # ==========================================================
    if analyze:

        with st.spinner("Reading and analyzing resume..."):
            result = extract_resume_text(uploaded_file)

        if result["success"]:

            st.success("✅ Resume parsed successfully!")

            candidate_information = extract_candidate_information(
                result["text"]
            )

            search_query = build_candidate_query(
                candidate_information
            )

            analysis_result = analyze_resume(
                candidate_information
            )

            # Save everything in Session State
            st.session_state.candidate_information = candidate_information
            st.session_state.search_query = search_query
            st.session_state.analysis_result = analysis_result
            st.session_state.resume_text = result["text"]

        else:
            st.error(result["error"])

    # ==========================================================
    # Display Analysis (Persists after reruns)
    # ==========================================================
    if st.session_state.candidate_information:

        find_jobs = display_resume_analysis(
            st.session_state.candidate_information,
            st.session_state.search_query,
            st.session_state.analysis_result,
        )

        with st.expander("📄 View Raw Resume Text"):
            st.text_area(
                "Extracted Resume Text",
                st.session_state.resume_text,
                height=300,
            )

    return {
        "uploaded_file": uploaded_file,
        "candidate_information": st.session_state.candidate_information,
        "search_query": st.session_state.search_query,
        "find_jobs": find_jobs,
    }