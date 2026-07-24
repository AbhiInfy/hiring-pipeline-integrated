import streamlit as st

def render_sidebar():

    with st.sidebar:

        st.markdown(
            """
            <div style="padding-bottom:15px;">
                <h2 style="margin:0;">🤖 AI Hiring Pipeline</h2>
                <div style="color:#94A3B8;font-size:14px;margin-top:4px;">
                    Integrated Recruitment System
                </div>
            </div>
            """,
            unsafe_allow_html=True,
)
        st.divider()
        st.markdown(
            "<p style='font-size:12px;color:#94A3B8;font-weight:600;'>NAVIGATION</p>",
        unsafe_allow_html=True,
        )

        st.button("🏠 Dashboard", use_container_width=True, key="sidebar_dashboard")

        st.button("👥 Candidates", use_container_width=True, key="sidebar_candidates")

        st.button("📄 Resume Analysis", use_container_width=True, key="sidebar_resume_analysis")

        st.button("🎯 Job Matching", use_container_width=True, key="sidebar_job_matching")

        st.button("📊 Reports", use_container_width=True, key="sidebar_reports")

        st.button("⚙️ Settings", use_container_width=True, key="sidebar_settings")

        st.divider()

        st.markdown(
            "<p style='font-size:12px;color:#94A3B8;font-weight:600;'>QUICK ACTIONS</p>",
            unsafe_allow_html=True,
        )

        st.button("⬆ Upload Resume", use_container_width=True, key="sidebar_upload_resume")

        st.button("➕ Analyze Resume", use_container_width=True, key="sidebar_analyze_resume")

        st.button("💼 View Jobs", use_container_width=True, key="sidebar_view_jobs")

        st.divider()

        st.markdown("""
        <div style="
        background:#1E293B;
        padding:15px;
        border-radius:12px;
        margin-top:10px;
        ">

        <b>👤 Admin User</b><br>

        <span style="color:#94A3B8;">
        Recruiter
        </span>

        </div>
        """, unsafe_allow_html=True)