# Hiring Pipeline (Integrated)

End-to-end hiring workflow with five connected stages:

1. Job ingestion from Naukri (Playwright browser automation)
2. JD catalog generation from collected links (adapter or heuristic)
3. Candidate-to-JD matching (adapter semantic matching or Jaccard fallback)
4. Email dispatch (dry-run by default, SMTP/SendGrid when enabled)
5. Recruiter dashboard in Streamlit

## Architecture

```text
Job Ingestion -> JD Generation -> Matching Engine -> Email Dispatch -> Dashboard
```

## Architecture Documentation
## System Architecture Diagram

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              HIRING PIPELINE SYSTEM                                  │
│                                                                                      │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   STAGE 1    │    │   STAGE 2    │    │   STAGE 3    │    │   STAGE 4    │       │
│  │    Job       │───▶│  Candidate   │───▶│  Matching    │───▶│   Email      │       │
│  │  Ingestion   │    │   Database   │    │   Engine     │    │  Dispatch    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘       │
│         │                   │                   │                   │               │
│         ▼                   ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Naukri     │    │   Excel      │    │  Jaccard     │    │   SMTP/      │       │
│  │   Web Scrape │    │   File       │    │  Similarity  │    │  SendGrid    │       │
│  └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘       │
│                                                   │                                   │
│                                                   ▼                                   │
│                                          ┌──────────────┐    ┌──────────────┐       │
│                                          │   STAGE 5    │    │  Streamlit   │       │
│                                          │  Dashboard   │◀───│    Web UI    │       │
│                                          └──────────────┘    └──────────────┘       │
└─────────────────────────────────────────────────────────────────────────────────────┘

## Detailed Component Architecture

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              INPUT LAYER                                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────┐    ┌─────────────────────────────────────────┐         │
│  │   Job Sources           │    │   Candidate Sources                      │         │
│  │   • Naukri.com          │    │   • Excel (.xlsx, .xls)                  │         │
│  │   • Custom Keywords     │    │   • CSV (auto-converted)                 │         │
│  │   • Search Pages        │    │   • Multiple sheets support              │         │
│  └─────────────────────────┘    └─────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              PROCESSING LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                      STAGE 1: JOB INGESTION                                   │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐   │    │
│  │  │  Playwright Browser Automation                                        │   │    │
│  │  │  • Headless/Non-headless mode                                        │   │    │
│  │  │  • Persistent profile support                                        │   │    │
│  │  │  • Age-based filtering (max-age-hours)                               │   │    │
│  │  │  • Manual login option                                               │   │    │
│  │  └──────────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                          │                                           │
│                                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                      STAGE 2: CANDIDATE DATABASE                              │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐   │    │
│  │  │  Excel File Processor                                                  │   │    │
│  │  │  • Column mapping (auto-detection)                                    │   │    │
│  │  │  • Multi-line skills extraction                                       │   │    │
│  │  │  • Data validation & cleaning                                         │   │    │
│  │  │  • Duplicate removal                                                  │   │    │
│  │  └──────────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                          │                                           │
│                                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                      STAGE 3: MATCHING ENGINE                                 │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐   │    │
│  │  │  Two Matching Strategies                                              │   │    │
│  │  │  ┌─────────────────────────┐  ┌─────────────────────────┐            │   │    │
│  │  │  │   Jaccard Similarity    │  │   Adapter Matching      │            │   │    │
│  │  │  │   • Text-based          │  │   • Semantic matching   │            │   │    │
│  │  │  │   • Fast & reliable     │  │   • More accurate       │            │   │    │
│  │  │  │   • No external deps    │  │   • Requires external   │            │   │    │
│  │  │  └─────────────────────────┘  └─────────────────────────┘            │   │    │
│  │  │                                                                       │   │    │
│  │  │  Auto mode: Tries adapter → Falls back to Jaccard                     │   │    │
│  │  └──────────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                          │                                           │
│                                          ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                      STAGE 4: EMAIL DISPATCH                                  │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐   │    │
│  │  │  Email Service                                                        │   │    │
│  │  │  ┌─────────────────────────┐  ┌─────────────────────────┐            │   │    │
│  │  │  │   SMTP (Gmail, etc)     │  │   SendGrid API          │            │   │    │
│  │  │  │   • TLS/SSL support     │  │   • REST API            │            │   │    │
│  │  │  │   • App passwords       │  │   • API key auth        │            │   │    │
│  │  │  └─────────────────────────┘  └─────────────────────────┘            │   │    │
│  │  │                                                                       │   │    │
│  │  │  Features:                                                           │   │    │
│  │  │  • Dry-run mode (default)                                            │   │    │
│  │  │  • Job-based filtering (only matching jobs)                          │   │    │
│  │  │  • Template-based email body                                         │   │    │
│  │  │  • Top 3 candidates per email                                        │   │    │
│  │  └──────────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT LAYER                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                         STAGE 5: DASHBOARD                                    │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐   │    │
│  │  │  Streamlit Web Application                                            │   │    │
│  │  │  • Real-time data visualization                                       │   │    │
│  │  │  • Candidate-job match analysis                                       │   │    │
│  │  │  • Email dispatch logs                                                │   │    │
│  │  │  • Pipeline metrics & KPIs                                            │   │    │
│  │  └──────────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                         GENERATED FILES                                       │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐   │    │
│  │  │  • job_links.xlsx         - Raw scraped job links                    │   │    │
│  │  │  • jd_catalog.csv         - Generated job descriptions               │   │    │
│  │  │  • shortlisted_profiles.csv - Matching results with scores           │   │    │
│  │  │  • email_dispatch.csv     - Email sending logs                       │   │    │
│  │  │  • pipeline_summary.json  - Complete execution summary               │   │    │
│  │  └──────────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘

## Data Flow Diagram
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA FLOW                                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

    Naukri.com                    Excel File                    Email Server
         │                             │                             │
         │ Job Listings                │ Candidate Profiles         │ Email
         ▼                             ▼                             ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  Stage 1        │           │  Stage 2        │           │  Stage 4        │
│  ┌───────────┐  │           │  ┌───────────┐  │           │  ┌───────────┐  │
│  │ Playwright│  │           │  │ Pandas    │  │           │  │ SMTP/     │  │
│  │ Scraper   │  │           │  │ Reader    │  │           │  │ SendGrid  │  │
│  └─────┬─────┘  │           │  └─────┬─────┘  │           │  └─────┬─────┘  │
└────────│────────┘           └────────│────────┘           └────────│────────┘
         │                             │                             │
         │ job_links.xlsx              │ candidate_profiles.xlsx     │ Email
         ▼                             ▼                             │
┌─────────────────────────────────────────────────────────────────────│────────────┐
│                              Stage 3                                 │            │
│  ┌──────────────────────────────────────────────────────────────────│────────┐   │
│  │                         Matching Engine                           │        │   │
│  │  ┌────────────────────────────────────────────────────────────┐  │        │   │
│  │  │  For each job:                                             │  │        │   │
│  │  │    For each candidate:                                     │  │        │   │
│  │  │      similarity = compare(skills, job_description)        │  │        │   │
│  │  │      if similarity >= min_score:                           │  │        │   │
│  │  │        add_to_matches()                                    │  │        │   │
│  │  └────────────────────────────────────────────────────────────┘  │        │   │
│  └──────────────────────────────────────────────────────────────────│────────┘   │
│                                                                      │             │
│                              shortlisted_profiles.csv                │             │
│                              (matches with scores)                   │             │
└──────────────────────────────────────────────────────────────────────│─────────────┘
                                                                       │
                                                                       ▼
                                                              ┌─────────────────┐
                                                              │  Stage 5        │
                                                              │  ┌───────────┐  │
                                                              │  │ Streamlit │  │
                                                              │  │ Dashboard │  │
                                                              │  └───────────┘  │
                                                              └─────────────────┘

## Technology Stack
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              TECHNOLOGY STACK                                        │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  BACKEND                                                                    │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │    │
│  │  │  • Python 3.10+                                                       │  │    │
│  │  │  • Pandas - Data manipulation                                         │  │    │
│  │  │  • NumPy - Numerical operations                                       │  │    │
│  │  │  • scikit-learn - Text similarity (Jaccard)                          │  │    │
│  │  └──────────────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  WEB SCRAPING                                                               │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │    │
│  │  │  • Playwright - Browser automation                                   │  │    │
│  │  │  • Chromium - Browser engine                                         │  │    │
│  │  └──────────────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  EMAIL SERVICES                                                             │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │    │
│  │  │  • SMTP (smtplib) - Gmail, Outlook, etc                              │  │    │
│  │  │  • SendGrid API - REST API integration                               │  │    │
│  │  │  • MIME - Email formatting                                           │  │    │
│  │  └──────────────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  FRONTEND                                                                   │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │    │
│  │  │  • Streamlit - Interactive dashboard                                 │  │    │
│  │  │  • Pandas - Data display                                             │  │    │
│  │  │  • CSV/JSON - Data interchange                                       │  │    │
│  │  └──────────────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  DATA STORAGE                                                               │    │
│  │  ┌──────────────────────────────────────────────────────────────────────┐  │    │
│  │  │  • Excel (.xlsx) - Job links & candidates                            │  │    │
│  │  │  • CSV - JD catalog & matches                                        │  │    │
│  │  │  • JSON - Pipeline summary                                           │  │    │
│  │  └──────────────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘

## Matching Algorithm Details

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         MATCHING ALGORITHM                                           │
└─────────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │  Candidate      │
                              │  Skills Text    │
                              └────────┬────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │  Tokenization   │
                              │  (split by      │
                              │   spaces/punctuation)
                              └────────┬────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
            ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
            │  Jaccard     │   │  Adapter     │   │  Auto        │
            │  Similarity  │   │  Matching    │   │  Mode        │
            │              │   │              │   │              │
            │  J(A,B) =    │   │  Semantic    │   │  Try adapter │
            │  |A∩B|/|A∪B| │   │  matching    │   │  ↓ if fails  │
            │              │   │  with        │   │  use Jaccard │
            │  Score:      │   │  embeddings  │   │              │
            │  0.0 - 1.0   │   │              │   │  Score:      │
            └──────┬───────┘   └──────┬───────┘   │  0.0 - 1.0   │
                   │                  │           └──────┬───────┘
                   └──────────────────┼──────────────────┘
                                      │
                                      ▼
                              ┌─────────────────┐
                              │  Score Filter   │
                              │  >= min_score   │
                              │  (default 0.12) │
                              └────────┬────────┘
                                       │
                          ┌────────────┼────────────┐
                          │            │            │
                          ▼            ▼            ▼
                  ┌────────────┐ ┌────────────┐ ┌────────────┐
                  │  Top-K     │ │  Sort by   │ │  Output    │
                  │  Filter    │ │  Score     │ │  Matches   │
                  │  (default 5)│ │  Descending│ │  to CSV    │
                  └────────────┘ └────────────┘ └────────────┘

## Email Flow Architecture

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           EMAIL DISPATCH FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

    matches_df                    jd_catalog_df
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  Filter jobs    │
              │  with matches   │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  For each job:  │
              │  Get top 3      │
              │  candidates     │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Build email    │
              │  from template  │
              └────────┬────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
         ▼             ▼             ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐
   │ Dry-run  │  │  SMTP    │  │ SendGrid │
   │ Mode     │  │  Send    │  │ API Send │
   │ (log     │  │          │  │          │
   │  only)   │  └────┬─────┘  └────┬─────┘
   └────┬─────┘       │             │
        │             └──────┬──────┘
        │                    │
        ▼                    ▼
   ┌─────────────────────────────────┐
   │  Update email_dispatch.csv      │
   │  with status:                   │
   │  • sent / failed / dry-run      │
   └─────────────────────────────────┘

## Deployment Architecture

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT ARCHITECTURE                                    │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────────────────────────┐
    │                         LOCAL/WINDOWS DEPLOYMENT                            │
    │                                                                              │
    │  ┌─────────────────────────────────────────────────────────────────────┐    │
    │  │                         Windows Machine                              │    │
    │  │                                                                       │    │
    │  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │    │
    │  │  │   Virtual       │    │   Python        │    │   Playwright    │   │    │
    │  │  │   Environment   │───▶│   Runtime       │───▶│   Browser       │   │    │
    │  │  │   (.venv)       │    │   (3.10+)       │    │   (Chromium)    │   │    │
    │  │  └─────────────────┘    └─────────────────┘    └─────────────────┘   │    │
    │  │                                                                       │    │
    │  │  ┌─────────────────────────────────────────────────────────────┐     │    │
    │  │  │                      Data Storage                           │     │    │
    │  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │     │    │
    │  │  │  │  Excel   │  │   CSV    │  │   JSON   │  │ Profiles │    │     │    │
    │  │  │  │  Files   │  │  Files   │  │  Files   │  │  Folder  │    │     │    │
    │  │  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │     │    │
    │  │  └─────────────────────────────────────────────────────────────┘     │    │
    │  │                                                                       │    │
    │  │  ┌─────────────────────────────────────────────────────────────┐     │    │
    │  │  │                    External Services                        │     │    │
    │  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │     │    │
    │  │  │  │ Naukri   │  │ Gmail    │  │ SendGrid │                  │     │    │
    │  │  │  │ Website  │  │ SMTP     │  │ API      │                  │     │    │
    │  │  │  └──────────┘  └──────────┘  └──────────┘                  │     │    │
    │  │  └─────────────────────────────────────────────────────────────┘     │    │
    │  └─────────────────────────────────────────────────────────────────────┘    │
    └─────────────────────────────────────────────────────────────────────────────┘

## Component Interaction Sequence
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        SEQUENCE DIAGRAM                                              │
└─────────────────────────────────────────────────────────────────────────────────────┘

    User          Pipeline         Naukri         Excel         Matching       Email
     │               │               │              │             │            │
     │───Run─────────▶│               │              │             │            │
     │               │───Scrape──────▶│              │             │            │
     │               │◀──Jobs────────│              │             │            │
     │               │               │              │             │            │
     │               │───────────────Load───────────▶│             │            │
     │               │◀────────────Candidates───────│             │            │
     │               │               │              │             │            │
     │               │──────────────Generate JD──────────────────▶│            │
     │               │               │              │             │            │
     │               │──────────────Match────────────────────────▶│            │
     │               │               │              │             │            │
     │               │──────────────Save Results──────────────────│            │
     │               │               │              │             │            │
     │               │──────────────Send Email────────────────────────────────▶│
     │               │               │              │             │            │
     │               │◀───────────────────────────────────────────Confirmation│
     │               │               │              │             │            │
     │◀──Complete────│               │              │             │            │

# Hiring Pipeline (Integrated)

End-to-end hiring workflow with five connected stages:

1. **Job ingestion** from Naukri (Playwright browser automation)
2. **JD catalog generation** from collected links (adapter or heuristic)
3. **Candidate-to-JD matching** (adapter semantic matching or Jaccard fallback)
4. **Email dispatch** (dry-run by default, SMTP/SendGrid when enabled)
5. **Recruiter dashboard** in Streamlit

Complete Setup Guide
Step 1: Clone or Download the Repository
powershell
git clone https://github.com/AbhiInfy/hiring-pipeline-integrated.git
cd hiring-pipeline-integrated
Step 2: Create and Activate Virtual Environment
powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
You should see (.venv) appear at the beginning of your prompt.

Step 3: Install Dependencies
powershell
pip install -r requirements.txt
If requirements.txt doesn't exist or is incomplete, install manually:

powershell
pip install pandas openpyxl numpy scikit-learn streamlit playwright python-dotenv
Step 4: Install Playwright Browser
powershell
python -m playwright install chromium
Step 5: Configure Environment Variables
Create .env file from the example:

powershell
Copy-Item .env.example .env
Edit .env with your values:

powershell
notepad .env
Required environment variables:

env
# SMTP Configuration (for Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-character-app-password

# SendGrid Configuration (alternative to SMTP)
SENDGRID_API_KEY=your-sendgrid-api-key
SENDGRID_SENDER_EMAIL=sender@example.com

# Email Recipients
PIPELINE_NOTIFICATION_EMAIL=recruiter@example.com
DEFAULT_FALLBACK_RECIPIENT=recruiter@example.com

# Email Customization (optional)
MAIL_SENDER_NAME=Your Name
MAIL_SENDER_TITLE=Your Title
Important for Gmail:

Enable 2-Factor Authentication on your Google account

Generate an App Password (16 characters)

Use the App Password as SENDER_PASSWORD (not your regular password)

Step 6: Prepare Candidate Excel File
Create an Excel file at output/candidate_profiles.xlsx with the following structure:

candidate_name	skills	email	notice_period_days
John Doe	Oracle Fusion, SQL, PLSQL	john@example.com	30
Jane Smith	Oracle EBS, Fusion Financials, GL	jane@example.com	Immediate
Accepted column name variations (auto-mapped):

Candidate Name → candidate_name

Skill or Skills → skills

Email ID or Email → email

Notice Period (Days) → notice_period_days

Note: The pipeline supports multi-line text in the Skills column (automatically cleaned and formatted).

Running the Pipeline
Basic Commands
1. Dry Run (No Emails, Default Settings)
powershell
python run_integrated_pipeline.py
2. Run with Custom Keyword and Pages
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 5
3. Run with Email Sending (SMTP)
powershell
python run_integrated_pipeline.py --send-emails --email-provider smtp --notification-email recruiter@example.com
4. Run with Email Sending (SendGrid)
powershell
python run_integrated_pipeline.py --send-emails --email-provider sendgrid --notification-email recruiter@example.com
Advanced Commands
Custom Matching Threshold
Lower threshold to get more matches (default is 0.12):

powershell
python run_integrated_pipeline.py --min-score 0.05 --send-emails --notification-email recruiter@example.com
Force Heuristic Mode (More Reliable, No External Dependencies)
powershell
python run_integrated_pipeline.py --jd-mode heuristic --matching-mode jaccard --send-emails --notification-email recruiter@example.com
Force Adapter Mode (Better Matching, Requires project-job-generator)
powershell
python run_integrated_pipeline.py --jd-mode adapter --matching-mode adapter --job-generator-dir ..\project-job-generator --send-emails --notification-email recruiter@example.com
Custom Candidate File Location
powershell
python run_integrated_pipeline.py --candidate-profiles-file "data\my_candidates.xlsx" --send-emails --notification-email recruiter@example.com
Manual Naukri Login (If Scraping Fails)
powershell
python run_integrated_pipeline.py --login --keyword "Oracle Fusion" --pages 3
Complete Production Command
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 3 --jd-mode auto --matching-mode auto --min-score 0.05 --top-k 5 --send-emails --email-provider smtp --notification-email recruiter@example.com
Using Windows Batch Files
The repository includes two batch files for convenience:

Run Pipeline
powershell
.\Run_Integrated_Pipeline.bat --keyword "Oracle Fusion" --pages 3 --send-emails --notification-email recruiter@example.com
Launch Dashboard
powershell
.\Run_Dashboard.bat
Fixing Unicode/Encoding Issues on Windows
If you see errors with special characters (✓, ❌, ⚠️), set UTF-8 encoding before running:

powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING="utf-8"
chcp 65001
Or use this one-liner:

powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; $env:PYTHONIOENCODING="utf-8"; python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 3 --send-emails --notification-email recruiter@example.com
Complete CLI Options Reference
Option	Description	Default
--candidate-profiles-file	Path to candidate Excel workbook (.xlsx/.xls)	output/candidate_profiles.xlsx
--profile-dir	Path to persistent browser profile directory	output/naukri_browser_profile
--output	Job links workbook path	output/job_links.xlsx
--keyword	Search keyword for Naukri	Oracle Fusion Application
--pages	Number of pages to scan	3
--max-age-hours	Ignore older jobs	24
--delay	Delay between page scans (seconds)	2.0
--login	Pause for manual Naukri login	False
--skip-contact-details	Skip collecting contact details	False
--rows	Limit rows used for JD generation	None (all rows)
--jd-mode	JD generation mode: auto, heuristic, adapter	auto
--matching-mode	Matching mode: auto, jaccard, adapter	auto
--job-generator-dir	Path to project-job-generator for adapter mode	../project-job-generator
--top-k	Max shortlisted candidates per job	5
--min-score	Minimum similarity threshold (0.0 to 1.0)	0.12
--default-email	Fallback email for job links	chaturvedi.abhishek10@gmail.com
--email-provider	Email provider: smtp or sendgrid	smtp
--send-emails	Actually send emails (otherwise dry-run)	False
--notification-email	Explicit recipient for dispatch stage	"" (uses .env value)
Launch Dashboard
After running the pipeline, launch the Streamlit dashboard to visualize results:

powershell
streamlit run src/dashboard/app.py
Or using the batch file:

powershell
.\Run_Dashboard.bat
The dashboard will open in your web browser at http://localhost:8501.

Generated Output Files
After running the pipeline, the following files are created in the output directory:

File	Description
job_links.xlsx	Raw job links scraped from Naukri
jd_catalog.csv	Generated job descriptions
shortlisted_profiles.csv	Candidate-to-job matches with similarity scores
email_dispatch.csv	Email dispatch log with status
pipeline_summary.json	Complete pipeline execution summary
candidate_profiles.xlsx	Input candidate file (auto-created if missing)
naukri_browser_profile/	Playwright browser session data
Email Dispatch Logic
When Emails Are Sent
Emails are only dispatched when ALL conditions are met:

✅ Valid candidate profiles loaded from Excel

✅ At least one candidate matches a job above the --min-score threshold

✅ --send-emails flag provided

✅ Recipient email configured (via .env or --notification-email)

Email Filtering
The pipeline automatically filters to send emails only for jobs that have matching candidates:

text
============================================================
📧 EMAIL DISPATCH FILTER
============================================================
Total jobs in catalog:     25
Jobs with matching candidates: 8
Jobs without any matches:  17

✅ Will send emails only for 8 job(s) that have candidates.
❌ Skipping 17 job(s) with no matching candidates.
Email Subject Format
text
Shortlist Update: {Job Title} - {Company Name}
If company name is missing, it defaults to "Client".

Email Delivery Verification
After each run, verify delivery status from output files:

output/email_dispatch.csv
Status	Meaning
sent	Email accepted by provider
dry-run	No real send attempted (default)
failed	Send failed (check message column)
skipped	No recipient configured or no matches
output/pipeline_summary.json
json
{
  "total_jobs": 25,
  "total_candidates": 13,
  "total_matches": 89,
  "emails_sent": 8,
  "emails_failed": 0,
  "emails_dry_run": 0,
  "requested_jd_mode": "auto",
  "used_jd_mode": "adapter",
  "requested_matching_mode": "auto",
  "used_matching_mode": "adapter",
  "warnings": []
}
If you do not see a message in inbox even when status=sent, check Spam/Promotions and sender-side Sent Mail.

Important Runtime Behavior
Stage 1 launches Chromium in non-headless mode to scrape Naukri.

By default, email stage is dry-run unless --send-emails is provided.

In auto mode, adapter components are attempted first and the pipeline falls back to heuristic/jaccard with warnings.

Job link output receives fallback email values where link-level email is missing.

Email filtering ensures only jobs with matching candidates receive emails.

Troubleshooting Guide
Setup Issues
Issue	Solution
ModuleNotFoundError	Run pip install -r requirements.txt
Playwright browser missing	Run python -m playwright install chromium
Virtual environment not activating	Run Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Unicode/encoding errors	Set UTF-8 encoding (see above)
Candidate File Issues
Issue	Solution
File not found	Create output/candidate_profiles.xlsx
Invalid file format	Use .xlsx or .xls only (no CSV)
Missing columns	Add: candidate_name, skills, email, notice_period_days
No valid candidates	Ensure at least one row has name and skills
File open error	Close Excel and re-run
Matching Issues
Issue	Solution
No matches found	Lower --min-score to 0.05 or 0.04
Too many matches	Increase --min-score to 0.15 or higher
Adapter mode failing	Use --matching-mode jaccard
JD generation failing	Use --jd-mode heuristic
Email Issues
Issue	Solution
No emails sent	Add --send-emails flag
SMTP auth errors	Use Gmail App Password, not regular password
Missing recipient	Set PIPELINE_NOTIFICATION_EMAIL in .env or use --notification-email
553 Invalid address	Ensure email has @domain.com format
Company name shows 'nan'	Fixed in latest version - defaults to "Client"
Gmail SMTP Configuration
For Gmail to work:

Enable 2-Factor Authentication on your Google account

Generate an App Password:

Go to Google Account → Security → App Passwords

Select "Mail" and "Windows Computer"

Copy the 16-character password

Use App Password in .env as SENDER_PASSWORD

Best Practices
Always use a virtual environment to avoid dependency conflicts

Test with dry-run first (--send-emails not included)

Start with lower page count (--pages 1) for initial testing

Use heuristic/jaccard mode if adapter mode fails

Lower --min-score gradually from 0.12 → 0.08 → 0.05

Check shortlisted_profiles.csv before sending emails

Verify email configuration with a simple test script

Close Excel files before running the pipeline

Example Workflow
Step 1: Initial Test (No Emails)
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 1 --rows 5
Step 2: Check Results
powershell
Import-Csv output\shortlisted_profiles.csv | Select-Object -First 10
Step 3: Adjust Threshold if Needed
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 3 --min-score 0.05
Step 4: Send Emails
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 3 --min-score 0.05 --send-emails --notification-email recruiter@example.com
Step 5: Launch Dashboard
powershell
streamlit run src/dashboard/app.py
Support
If you encounter issues:

Check the troubleshooting guide above

Review output/pipeline_summary.json for warnings

Check output/email_dispatch.csv for email errors

Ensure all prerequisites are installed correctly

License
This project is open-source and available for use and modification.

text

This updated README includes:
- ✅ Complete architecture diagrams
- ✅ Detailed setup guide with all steps
- ✅ All possible command options and examples
- ✅ Email dispatch logic explanation
- ✅ Troubleshooting for common issues
- ✅ Gmail SMTP configuration instructions
- ✅ Unicode/encoding fixes for Windows
- ✅ Best practices and example workflow
- ✅ Full file content ready for copy-paste

## What this repository runs

- Main pipeline entrypoint: run_integrated_pipeline.py
- Dashboard entrypoint: src/dashboard/app.py
- Windows launchers:
  - Run_Integrated_Pipeline.bat
  - Run_Dashboard.bat

## Prerequisites

- Python 3.10+
- Windows PowerShell (examples below are PowerShell)
- Internet access for Naukri scraping and JD page fetch

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Install Playwright browser (required for Stage 1 scraping):

```powershell
python -m playwright install chromium
```

4. Configure environment values:

```powershell
Copy-Item .env.example .env
```

Then update .env with your values (especially if you will send emails):

- SMTP_SERVER
- SMTP_PORT
- SENDER_EMAIL
- SENDER_PASSWORD
- SENDGRID_API_KEY
- SENDGRID_SENDER_EMAIL
- PIPELINE_NOTIFICATION_EMAIL
- DEFAULT_FALLBACK_RECIPIENT

For Gmail SMTP, use a 16-character Google App Password for SENDER_PASSWORD.

## Candidate Input Format

The pipeline expects candidate profiles in an Excel workbook (.xlsx or .xls).

Default input path:

- output/candidate_profiles.xlsx

If this file does not exist, the pipeline seeds an empty workbook with required columns.

Required columns:

- candidate_name
- skills
- email
- notice_period_days

Also accepted (auto-mapped) headers:

- Candidate Name -> candidate_name
- Skill -> skills
- Email ID -> email
- Notice Period (Days) -> notice_period_days

## Run the Pipeline

Basic run (dry-run emails, default settings):

```powershell
python .\run_integrated_pipeline.py
```

Run with custom search and page count:

```powershell
python .\run_integrated_pipeline.py --keyword "Oracle Fusion Application" --pages 2 --rows 10
```

Run with adapter-backed JD generation (uses project-job-generator when available):

```powershell
python .\run_integrated_pipeline.py --jd-mode adapter --job-generator-dir ..\project-job-generator
```

Run with adapter-backed semantic candidate matching:

```powershell
python .\run_integrated_pipeline.py --matching-mode adapter --job-generator-dir ..\project-job-generator
```

Run with explicit Jaccard matching:

```powershell
python .\run_integrated_pipeline.py --matching-mode jaccard
```

Run with explicit heuristic JD generation:

```powershell
python .\run_integrated_pipeline.py --jd-mode heuristic
```

Run with manual Naukri login flow:

```powershell
python .\run_integrated_pipeline.py --login --keyword "Oracle Fusion Application" --pages 2
```

Run using a custom candidate workbook:

```powershell
python .\run_integrated_pipeline.py --candidate-profiles-file .\data\candidate_profiles.xlsx
```

Tune matching strictness:

```powershell
python .\run_integrated_pipeline.py --top-k 5 --min-score 0.15 --rows 20
```

Send real emails via SMTP:

```powershell
python .\run_integrated_pipeline.py --send-emails --email-provider smtp --notification-email recruiter@example.com
```

Example verified send command:

```powershell
python .\run_integrated_pipeline.py --pages 1 --rows 1 --skip-contact-details --jd-mode auto --matching-mode auto --job-generator-dir ..\project-job-generator --send-emails --email-provider smtp --notification-email recruiter@example.com --keyword "Oracle Fusion Application"
```

Send real emails via SendGrid:

```powershell
python .\run_integrated_pipeline.py --send-emails --email-provider sendgrid --notification-email recruiter@example.com
```

Windows launcher:

```powershell
.\Run_Integrated_Pipeline.bat --keyword "Oracle Fusion Application" --pages 2
```

## Launch Dashboard

```powershell
python -m streamlit run src\dashboard\app.py
```

Or:

```powershell
.\Run_Dashboard.bat
```

## Generated Outputs

- output/job_links.xlsx
- output/jd_catalog.csv
- output/shortlisted_profiles.csv
- output/email_dispatch.csv
- output/pipeline_summary.json

Notes:

- output/candidate_profiles.xlsx is an input workbook (auto-seeded when missing).
- output/naukri_browser_profile stores Playwright persistent browser session data.

## Important Runtime Behavior

- Stage 1 launches Chromium in non-headless mode to scrape Naukri.
- By default, email stage is dry-run unless --send-emails is provided.
- In auto mode, adapter components are attempted first and the pipeline falls back to heuristic/jaccard with warnings.
- Job link output receives fallback email values where link-level email is missing.

## Email Delivery Verification

After each run, verify delivery status from output files:

- output/email_dispatch.csv
  - status=sent means the email provider accepted the message
  - status=dry-run means no real send was attempted
  - status=failed means send attempt failed and message contains error details
- output/pipeline_summary.json
  - emails_sent / emails_failed / emails_dry_run counters
  - requested_* and used_* mode fields for JD and matching
  - warnings list when auto-mode fallback occurred

If you do not see a message in inbox even when status=sent, check Spam/Promotions and sender-side Sent Mail.

## CLI Options

```text
--candidate-profiles-file   Path to candidate Excel workbook (.xlsx/.xls)
--profile-dir               Path to persistent browser profile directory
--output                    Job links workbook path (default: output/job_links.xlsx)
--keyword                   Search keyword (default: Oracle Fusion Application)
--pages                     Number of pages to scan (default: 3)
--max-age-hours             Ignore older jobs (default: 24)
--delay                     Delay between page scans (default: 2.0)
--login                     Pause for manual Naukri login before scraping
--rows                      Limit rows used for JD generation
--jd-mode                   auto | heuristic | adapter (default: auto)
--matching-mode             auto | jaccard | adapter (default: auto)
--job-generator-dir         Path to project-job-generator for adapter mode
--top-k                     Max shortlisted candidates per job (default: 5)
--min-score                 Minimum similarity threshold (default: 0.12)
--default-email             Fallback email written to job link rows
--email-provider            smtp | sendgrid (default: smtp)
--send-emails               Actually send emails (otherwise dry-run)
--notification-email        Explicit recipient override for dispatch stage
```

## Troubleshooting

- ModuleNotFoundError (for example: pandas): install dependencies with pip install -r requirements.txt.
- Playwright browser missing: run python -m playwright install chromium.
- Adapter mode not found: pass --job-generator-dir to your project-job-generator path, or use --jd-mode heuristic.
- Matching adapter issues: use --matching-mode jaccard, or install project-job-generator dependencies in the active environment.
- No dashboard data: run the pipeline first to generate output/shortlisted_profiles.csv.
- No email recipient configured: set PIPELINE_NOTIFICATION_EMAIL or DEFAULT_FALLBACK_RECIPIENT, or pass --notification-email.
- Email not received: first check output/email_dispatch.csv. If status is dry-run, rerun with --send-emails. If status is failed, read message for SMTP/SendGrid error.
- Gmail SMTP auth errors: ensure SENDER_EMAIL is correct, 2FA is enabled, and SENDER_PASSWORD is a valid App Password.
