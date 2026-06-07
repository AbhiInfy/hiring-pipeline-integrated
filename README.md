# Hiring Pipeline (Integrated)

End-to-end hiring workflow with five connected stages:

1. Job ingestion from Naukri (Playwright browser automation)
2. JD catalog generation from collected links
3. Candidate-to-JD matching (Jaccard score on normalized skill tokens)
4. Email dispatch (dry-run by default, SMTP/SendGrid when enabled)
5. Recruiter dashboard in Streamlit

## Architecture

```text
Job Ingestion -> JD Generation -> Matching Engine -> Email Dispatch -> Dashboard
```

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
- Job link output receives fallback email values where link-level email is missing.

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
- No dashboard data: run the pipeline first to generate output/shortlisted_profiles.csv.
- No email recipient configured: set PIPELINE_NOTIFICATION_EMAIL or DEFAULT_FALLBACK_RECIPIENT, or pass --notification-email.
