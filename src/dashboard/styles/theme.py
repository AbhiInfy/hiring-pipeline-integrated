import streamlit as st


def load_theme():
    st.markdown(
        """
        <style>

        /* =========================
           GLOBAL
        ========================== */

        :root{
            --bg:#0F172A;
            --card:#1E293B;
            --card-hover:#273549;

            --primary:#4F7CFF;
            --success:#22C55E;
            --warning:#F59E0B;
            --danger:#EF4444;

            --text:#FFFFFF;
            --text-secondary:#94A3B8;

            --border:#334155;
            --radius:14px;
        }

        /* =========================
           APP
        ========================== */

        .stApp{
            background:var(--bg);
            color:var(--text);
        }

        .main .block-container{
            max-width:1500px;
            padding-top:2rem;
            padding-left:2rem;
            padding-right:2rem;
            padding-bottom:2rem;
        }

        /* =========================
           TYPOGRAPHY
        ========================== */

        h1,h2,h3,h4,h5,h6{
            color:var(--text);
            font-weight:700;
        }

        p,label{
            color:var(--text-secondary);
        }

        hr{
            border-color:var(--border);
        }

        /* =========================
           METRIC CARDS
        ========================== */

        div[data-testid="stMetric"]{

            background:var(--card);

            border:1px solid var(--border);

            padding:18px;

            border-radius:14px;

            transition:.25s;

        }

        div[data-testid="stMetric"]:hover{

            border-color:var(--primary);

            transform:translateY(-2px);

        }

        div[data-testid="stMetricLabel"]{

            color:var(--text-secondary);

            font-size:14px;

        }

        div[data-testid="stMetricValue"]{

            color:white;

            font-weight:700;

        }

        /* =========================
           BUTTONS
        ========================== */

        /* BUTTON */

        .stButton > button {

            background: #4F7CFF !important;

            color: black !important;

            font-weight: 700 !important;

            font-size: 16px !important;

            border: none !important;

            border-radius: 12px !important;

            height: 52px !important;
        }

        /* Force every child element inside the button */

        .stButton > button * {

            color: black !important;

            font-weight: 700 !important;

            fill: black !important;
        }

        /* Specifically target paragraph/span used by newer Streamlit */

        .stButton button span,
        .stButton button p {

            color: black !important;

            font-weight: 700 !important;

            font-size: 16px !important;
        }

        /* =========================
           FILE UPLOADER
        ========================== */

        div[data-testid="stFileUploader"]{

            background:var(--card);

            border:2px dashed var(--border);

            border-radius:14px;

            padding:18px;

        }

        /* =========================
           INPUT BOX
        ========================== */

        input{

            color:white !important;

        }

        /* =========================
           SELECTBOX
        ========================== */

        div[data-baseweb="select"]{

            background:var(--card);

            border-radius:10px;

        }

        /* =========================
           SIDEBAR
        ========================== */

        section[data-testid="stSidebar"]{

            background:#111827;

            border-right:1px solid var(--border);

        }

        section[data-testid="stSidebar"] *{

            color:white;

        }

        /* =========================
           ALERTS
        ========================== */

        div[data-testid="stSuccess"]{

            border-radius:12px;

        }

        div[data-testid="stInfo"]{

            border-radius:12px;

        }

        /* =========================
           TABLES
        ========================== */

        .stDataFrame{

            border-radius:14px;

            overflow:hidden;

        }

        /* =========================
           SCROLLBAR
        ========================== */

        ::-webkit-scrollbar{

            width:10px;

        }

        ::-webkit-scrollbar-track{

            background:#0f172a;

        }

        ::-webkit-scrollbar-thumb{

            background:#334155;

            border-radius:20px;

        }

        ::-webkit-scrollbar-thumb:hover{

            background:#4F7CFF;

        }

/* =========================
   ANALYSIS SUMMARY CARDS
========================= */

        .summary-card{

            background:#1E293B;

            border:1px solid #334155;

            border-radius:14px;

            padding:18px;

            height:90px;

            transition:.25s;

        }

        .summary-card:hover{

            border-color:#4F7CFF;

            transform:translateY(-2px);

        }

        .summary-title{

            color:#94A3B8;

            font-size:14px;

            margin-bottom:10px;

        }

        .summary-value{

            color:white;

            font-size:18px;

            font-weight:700;

        }

        

        </style>
        """,
        unsafe_allow_html=True,
    )