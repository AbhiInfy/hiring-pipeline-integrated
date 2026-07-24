import streamlit as st

print("SEARCH PANEL LOADED")


def render_search_panel():

    st.markdown("## 🔍 Smart Hiring Search")
    st.caption(
        "Search for candidates by entering a job role and pipeline parameters."
    )

    # Seed defaults once so placeholders aren't mistaken for real values.
    if "search_min_score" not in st.session_state:
        st.session_state["search_min_score"] = 0.01
    if "search_top_k" not in st.session_state:
        st.session_state["search_top_k"] = 5

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        keyword = st.text_input(
            "Job Role",
            placeholder="e.g. Java Developer",
            key="search_keyword",
        )

    with col2:
        skills = st.text_input(
            "Skills",
            placeholder="e.g. Python, SQL, FastAPI",
            key="search_skills",
        )

    with col3:
        experience = st.selectbox(
            "Experience",
            [
                "Any",
                "0-2 Years",
                "2-5 Years",
                "5-8 Years",
                "8+ Years",
            ],
            key="search_experience",
        )

    with col4:
        location = st.selectbox(
            "Location",
            [
                "Any",
                "Remote",
                "Bangalore",
                "Hyderabad",
                "Pune",
                "Delhi",
            ],
            key="search_location",
        )

    col_a, col_b, col_c = st.columns(3)
    st.write("")

    with col_a:
        min_score = st.slider(
            "Minimum Match",
            0.0,
            1.0,
            step=0.01,
            key="search_min_score",
        )

    with col_b:
        pages = st.number_input(
            "Pages",
            min_value=1,
            max_value=20,
            value=3,
            key="search_pages",
        )

    with col_c:
        top_k = st.number_input(
            "Top Matches per Job",
            min_value=1,
            max_value=20,
            key="search_top_k",
            help="Maximum number of shortlisted candidates to keep for each job (top-k).",
        )
    st.write("")

    left_space, center_col, right_space = st.columns([1, 2, 1])

    with center_col:

        run = st.button(
            "🚀 Run AI Pipeline",
            use_container_width=True,
            key="search_run_button",
        )

    st.divider()

    return {
        "keyword": keyword,
        "skills": skills,
        "experience": experience,
        "location": location,
        "min_score": min_score,
        "pages": pages,
        "top_k": int(top_k),
        "run": run,
    }