import streamlit as st
from styles.theme import load_theme
from components.header import render_header
from components.search_panel import render_search_panel
from components.sidebar import render_sidebar
from components.metric_cards import render_metric_cards
from components.upload_panel import render_upload_panel
from components.pipeline_overview import render_pipeline_overview
from components.analysis_summary import render_analysis_summary
from components.jobs_panel import render_jobs_panel


st.set_page_config(
    page_title="AI Hiring Pipeline",
    page_icon="🤖",
    layout="wide"
)

load_theme()
render_sidebar()
render_header()
search_data = render_search_panel()

st.divider()

# ==========================
# KPI SECTION
# ==========================

render_metric_cards()
st.divider()

# ==========================
# SECOND ROW
# ==========================

upload_col, overview_col = st.columns([1.2,1])

with upload_col:
    uploaded_file = render_upload_panel()

with overview_col:
    render_pipeline_overview()


st.divider()

# ==========================
# THIRD ROW
# ==========================

summary_col, jobs_col = st.columns([1,1])

with summary_col:
    render_analysis_summary()


with jobs_col:
    render_jobs_panel()