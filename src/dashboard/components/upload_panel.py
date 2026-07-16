import streamlit as st


def render_upload_panel():
    """Render the resume upload and analysis section."""

    st.subheader("📄 Upload & Analyze Resume")
    st.caption(
    "Upload a resume file and let AI analyze it."
    )

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

    if analyze:
        with st.spinner("Analyzing resume..."):
            progress = st.progress(0)

            for value in [25, 50, 75, 100]:
                progress.progress(value)

        st.success("Resume analyzed successfully! (Backend integration coming next)")

    return uploaded_file