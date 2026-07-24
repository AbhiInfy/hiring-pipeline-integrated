import streamlit as st
import subprocess
import sys
from pathlib import Path
from styles.theme import load_theme
from components.header import render_header
from components.search_panel import render_search_panel
from components.sidebar import render_sidebar
from components.metric_cards import render_metric_cards
from components.upload_panel import render_upload_panel
from components.pipeline_overview import render_pipeline_overview
from components.analysis_summary import render_analysis_summary
from components.jobs_panel import render_jobs_panel


def _log(message: str = "") -> None:
    """Print to the Streamlit / terminal console with flush."""
    print(message, flush=True)


def _run_pipeline_streaming(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """Run pipeline and stream stdout/stderr live to the terminal console."""
    _log("\n" + "=" * 60)
    _log(" DASHBOARD → STARTING PIPELINE")
    _log("=" * 60)
    _log(" Command: " + " ".join(str(part) for part in command))
    _log("=" * 60 + "\n")

    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    collected: list[str] = []
    assert process.stdout is not None
    for line in process.stdout:
        collected.append(line)
        print(line, end="", flush=True)

    returncode = process.wait()
    output = "".join(collected)

    _log("\n" + "=" * 60)
    _log(f" DASHBOARD → PIPELINE EXIT CODE: {returncode}")
    _log("=" * 60 + "\n")

    return subprocess.CompletedProcess(
        args=command,
        returncode=returncode,
        stdout=output,
        stderr="",
    )


def _build_search_query(search_data: dict) -> str:
    """Build the same search query shape used by the pipeline."""
    query_parts = []
    for part in [
        search_data.get("keyword", ""),
        search_data.get("skills", ""),
        search_data.get("experience", ""),
        search_data.get("location", ""),
    ]:
        value = str(part).strip()
        if not value or value.lower() == "any":
            continue
        query_parts.append(value)
    return " ".join(query_parts)


def _build_search_query_from_state() -> str:
    """Build the current search query directly from Streamlit session state."""
    query_parts = []
    for key in ["search_keyword", "search_skills", "search_experience", "search_location"]:
        value = str(st.session_state.get(key, "")).strip()
        if not value or value.lower() == "any":
            continue
        query_parts.append(value)
    return " ".join(query_parts)


st.set_page_config(
    page_title="AI Hiring Pipeline",
    page_icon="🤖",
    layout="wide"
)

load_theme()
render_sidebar()
render_header()
search_data = render_search_panel()
current_search_query = _build_search_query_from_state() or _build_search_query(search_data)

if current_search_query:
    st.info(f"Current Search Query: {current_search_query}")
else:
    st.info("Current Search Query: (empty)")

if search_data["run"]:
    keyword = str(search_data.get("keyword") or "").strip()
    if not keyword:
        st.error("Job Role is required. Enter a role (e.g. python developer) before running.")
    else:
        search_query = _build_search_query(search_data) or keyword
        _log("\n" + "=" * 60)
        _log(" DASHBOARD SEARCH INPUTS")
        _log("=" * 60)
        _log(f" keyword    : {keyword!r}")
        _log(f" skills     : {search_data['skills']!r}")
        _log(f" experience : {search_data['experience']!r}")
        _log(f" location   : {search_data['location']!r}")
        _log(f" pages      : {search_data['pages']}")
        _log(f" min-score  : {search_data['min_score']}")
        _log(f" top-k      : {search_data['top_k']}")
        _log(f" query      : {search_query!r}")
        _log("=" * 60)

        with st.spinner("🚀 Running AI Hiring Pipeline..."):

            command = [
                sys.executable,
                "run_integrated_pipeline.py",
                "--keyword",
                keyword,
                "--skills",
                search_data["skills"],
                "--experience",
                search_data["experience"],
                "--location",
                search_data["location"],
                "--pages",
                str(search_data["pages"]),
                "--min-score",
                str(search_data["min_score"]),
                "--top-k",
                str(search_data["top_k"]),
                "--reset-job-links",
                "--send-emails",
                "--notification-email",
                "chaturvedi.abhishek10@gmail.com",
                "--use-embeddings",
                "--cache-embeddings",
            ]

            result = _run_pipeline_streaming(
                command,
                cwd=Path(__file__).resolve().parents[2],
            )

        if result.returncode == 0:
            st.success("✅ Pipeline completed successfully!")
            if result.stdout:
                with st.expander("Pipeline output"):
                    st.code(result.stdout)
            st.rerun()

        else:
            st.error("❌ Pipeline failed.")
            st.code(result.stderr or result.stdout or "No error output captured.")

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