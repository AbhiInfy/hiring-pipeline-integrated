import os
import pandas as pd
import streamlit as st


def render_recommended_jobs_panel():

    st.markdown("## 💼 Recommended Job Openings")

    file_path = "output/job_links.xlsx"

    if not os.path.exists(file_path):
        st.warning("No job openings found.")
        return

    try:
        df = pd.read_excel(file_path)

    except Exception as e:
        st.error(f"Unable to read job_links.xlsx\n\n{e}")
        return

    if df.empty:
        st.info("No job openings available.")
        return

    # -----------------------------
    # Clean Data
    # -----------------------------

    df = df.fillna("Not Available")

    # -----------------------------
    # Keep only required columns
    # -----------------------------

    display_df = pd.DataFrame()

    display_df["Job Title"] = df["Job Title"]
    display_df["Company"] = df["Company"]
    display_df["Posted"] = df["Posted"]
    display_df["Email"] = df["Email"]
    display_df["Apply"] = df["Job Link"]

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )