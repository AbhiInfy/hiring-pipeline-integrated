import streamlit as st


# ==========================================================
# Resume Analyzer
# ==========================================================

def analyze_resume(candidate_information):
    """
    Analyze extracted resume information and
    generate an overall resume quality score.
    """

    score = 0
    strengths = []
    missing = []

    # ------------------------------------------------------
    # Name
    # ------------------------------------------------------

    if candidate_information.get("name"):
        score += 10
    else:
        missing.append("Name")

    # ------------------------------------------------------
    # Email
    # ------------------------------------------------------

    if candidate_information.get("email"):
        score += 10
    else:
        missing.append("Email")

    # ------------------------------------------------------
    # Phone
    # ------------------------------------------------------

    if candidate_information.get("phone"):
        score += 10
    else:
        missing.append("Phone Number")

    # ------------------------------------------------------
    # Job Role
    # ------------------------------------------------------

    if candidate_information.get("role"):
        score += 15
        strengths.append("Clear Job Role")
    else:
        missing.append("Job Role")

    # ------------------------------------------------------
    # Experience
    # ------------------------------------------------------

    if candidate_information.get("experience"):
        score += 15
        strengths.append("Experience Mentioned")
    else:
        missing.append("Experience")

    # ------------------------------------------------------
    # Location
    # ------------------------------------------------------

    if candidate_information.get("location"):
        score += 10
    else:
        missing.append("Location")

    # ------------------------------------------------------
    # Skills
    # ------------------------------------------------------

    skills = candidate_information.get("skills", [])

    if len(skills) >= 10:
        score += 30
        strengths.append("Strong Technical Skillset")

    elif len(skills) >= 5:
        score += 20
        strengths.append("Good Technical Skills")

    elif len(skills) > 0:
        score += 10

    else:
        missing.append("Technical Skills")

    # ------------------------------------------------------
    # Recommendation
    # ------------------------------------------------------

    if score >= 85:
        recommendation = "Candidate appears job-ready."

    elif score >= 70:
        recommendation = "Resume is good with minor improvements."

    elif score >= 50:
        recommendation = "Resume is average. More details should be added."

    else:
        recommendation = "Resume requires significant improvements."

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    if score >= 85:
        status = "Excellent ✅"

    elif score >= 70:
        status = "Good 👍"

    elif score >= 50:
        status = "Average ⚠️"

    else:
        status = "Needs Improvement ❌"

    return {
        "score": score,
        "strengths": strengths,
        "missing": missing,
        "recommendation": recommendation,
        "status": status,
    }


# ==========================================================
# Resume Analysis UI
# ==========================================================

def display_resume_analysis(
    candidate_information,
    search_query,
    analysis_result,
):

    st.markdown("## 📄 Candidate Summary")

    skills = candidate_information.get("skills", [])

    skills_text = (
        " • ".join(skills)
        if skills
        else "Not Found"
    )

    st.markdown(
        f"""
<div style="
padding:12px 16px;
border-radius:10px;
background:#1E293B;
border:1px solid #334155;
margin-bottom:12px;
line-height:1.45;
">

<h4 style="margin:0 0 10px 0;">
👤 {candidate_information.get("name","Not Found")}
</h4>

<b>💼 Role:</b>
{candidate_information.get("role","Not Found")}

<br>

<b>📍 Location:</b>
{candidate_information.get("location","Not Found")}

<br>

<b>📧 Email:</b>
{candidate_information.get("email","Not Found")}

<br>

<b>📱 Phone:</b>
{candidate_information.get("phone","Not Found")}

<br>

<b>🛠 Skills</b>

<br>

{skills_text}

</div>
""",
        unsafe_allow_html=True,
    )

    score = analysis_result["score"]

    # ==========================================================
    # Resume Quality
    # ==========================================================

    st.markdown("## 📊 Resume Quality")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Resume Score",
            f"{score}/100",
        )

    with col2:
        st.metric(
            "Strengths",
            len(analysis_result["strengths"]),
        )

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "Missing Fields",
            len(analysis_result["missing"]),
        )

    with col4:
        st.metric(
            "Status",
            analysis_result["status"],
        )

    st.progress(score / 100)

    st.write("")

    # ==========================================================
    # Recommendation Banner
    # ==========================================================

    if score >= 85:
        border = "#16A34A"
        bg = "#052E16"

    elif score >= 70:
        border = "#2563EB"
        bg = "#172554"

    elif score >= 50:
        border = "#F59E0B"
        bg = "#451A03"

    else:
        border = "#DC2626"
        bg = "#450A0A"

    st.markdown(
        f"""
<div style="
padding:15px;
background:{bg};
border-left:6px solid {border};
border-radius:10px;
margin-top:15px;
margin-bottom:20px;
">

<b>💡 Recommendation</b>

<br><br>

{analysis_result["recommendation"]}

</div>
""",
        unsafe_allow_html=True,
    )

    # ==========================================================
    # Find Matching Jobs
    # ==========================================================

    find_jobs = st.button(
        "🔍 Find Matching Jobs",
        type="primary",
        use_container_width=True,
    )

    st.write("")

    # ==========================================================
    # Strengths
    # ==========================================================

    with st.expander("✅ Resume Strengths"):

        if analysis_result["strengths"]:

            for item in analysis_result["strengths"]:
                st.success(item)

        else:
            st.info("No strengths identified.")

    # ==========================================================
    # Missing Information
    # ==========================================================

    with st.expander("⚠ Missing Information"):

        if analysis_result["missing"]:

            for item in analysis_result["missing"]:
                st.warning(item)

        else:
            st.success("No important information is missing.")

    # ==========================================================
    # Advanced Details
    # ==========================================================

    with st.expander("⚙️ Advanced Details"):

        st.markdown("##### Generated Search Query")

        st.code(
            search_query,
            language="text",
        )

    # ==========================================================
    # Resume Preview (Optional)
    # ==========================================================

    if "resume_text" in st.session_state:

        with st.expander("📄 Raw Resume"):

            st.text_area(
                "Resume Content",
                st.session_state.resume_text,
                height=250,
                disabled=True,
                label_visibility="collapsed",
            )

    st.divider()

    return find_jobs