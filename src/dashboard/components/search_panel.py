import streamlit as st

print("SEARCH PANEL LOADED")


def render_search_panel():

    st.markdown("## 🔍 Smart Hiring Search")
    st.caption(
        "Search for candidates by entering a job role and pipeline parameters."
    )

    st.write("")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        keyword = st.text_input(
            "Job Role",
            placeholder="Python Developer",
        )

    with col2:
        skills = st.text_input(
             "Skills",
            placeholder="Python, SQL, FastAPI",
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
        )

    col4, col5 = st.columns(2)
    st.write("")

    with col4:
        min_score = st.slider(
            "Minimum Match",
            0.0,
            1.0,
            0.05,
            0.01,
        )

    with col5:
        pages = st.number_input(
            "Pages",
            min_value=1,
            max_value=20,
            value=3,
        )
    st.write("")

    left_space, center_col, right_space = st.columns([1,2,1])

    with center_col:

        run = st.button(
            "🚀 Run AI Pipeline",
            use_container_width=True,
        )

    st.divider()

    return {
        "keyword": keyword,
        "skills": skills,
        "experience": experience,
        "location": location,
        "min_score": min_score,
        "pages": pages,
        "run": run,
    }