# Hiring Pipeline (Integrated)

## Project Overview

The **Hiring Pipeline** is an end-to-end automated recruitment system that streamlines the entire hiring workflow from job discovery to candidate shortlisting and email dispatch. It integrates web scraping, intelligent matching, and automated communication into a single pipeline.

### Key Features

- **Automated Job Discovery**: Scrapes latest job postings from Naukri.com using Playwright browser automation
- **Smart Candidate Matching**: Uses Jaccard similarity and semantic matching algorithms to find the best candidates for each job
- **Automated Email Dispatch**: Sends personalized shortlists to recruiters with top matching candidates
- **Interactive Dashboard**: Streamlit-based dashboard for visualizing matches and pipeline metrics
- **Flexible Configuration**: Supports both heuristic (fast) and adapter (accurate) matching modes
- **Excel-Based Input**: Simple Excel file format for candidate data with flexible column mapping

### Use Cases

- Recruitment agencies managing multiple candidates across various job openings
- HR departments automating candidate-job matching
- Staffing firms needing quick shortlisting for multiple positions
- Internal recruitment teams looking to reduce manual screening time

### How It Works

The pipeline processes data through five sequential stages:
Stage 1: Job Ingestion → Scrapes jobs from Naukri.com
Stage 2: Candidate DB → Loads candidate profiles from Excel
Stage 3: Matching Engine → Matches candidates to jobs using similarity algorithms
Stage 4: Email Dispatch → Sends shortlists to recruiters (dry-run by default)
Stage 5: Dashboard → Visualizes results in Streamlit

text

## Architecture

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

## What This Repository Runs

Main pipeline entrypoint: run_integrated_pipeline.py

Dashboard entrypoint: src/dashboard/app.py

## Windows launchers:

Run_Integrated_Pipeline.bat - Launches the main pipeline

Run_Dashboard.bat - Launches the Streamlit dashboard

## Prerequisites
Python 3.10+ (Python 3.11 or 3.12 recommended)

Windows PowerShell (examples below are for PowerShell)

Internet access for Naukri scraping and JD page fetch

Gmail account (for SMTP email sending) or SendGrid account

## Complete Setup Guide
# Step 1: Clone or Download the Repository
powershell
git clone https://github.com/AbhiInfy/hiring-pipeline-integrated.git
cd hiring-pipeline-integrated
# Step 2: Create and Activate Virtual Environment
powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
You should see (.venv) appear at the beginning of your prompt.

# Step 3: Install Dependencies
powershell
pip install -r requirements.txt
If requirements.txt doesn't exist, install manually:

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
Required environment variables for email sending:

env
# SMTP Configuration (for Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-character-app-password

# Email Recipients
PIPELINE_NOTIFICATION_EMAIL=recruiter@example.com
DEFAULT_FALLBACK_RECIPIENT=recruiter@example.com

# Email Customization (optional)
MAIL_SENDER_NAME=Your Name
MAIL_SENDER_TITLE=Your Title
Important for Gmail:

Enable 2-Factor Authentication on your Google account

Generate an App Password (16 characters) at: Google Account → Security → App Passwords

Use the App Password as SENDER_PASSWORD (NOT your regular password)

Step 6: Prepare Candidate Excel File ⚠️ IMPORTANT
You MUST manually create this file. The pipeline will NOT create it for you!

Create an Excel file at output/candidate_profiles.xlsx with the following structure:

candidate_name	skills	email	notice_period_days
John Doe	Oracle Fusion, SQL, PLSQL	john@example.com	30
Jane Smith	Oracle EBS, Fusion Financials, GL	jane@example.com	Immediate
Mike Johnson	Oracle Cloud, Fusion HCM, Core HR	mike@example.com	15
📌 CRITICAL NOTES:

The pipeline will NOT auto-create this file with your data - it will only create an empty template if the file doesn't exist

You must manually create and populate this file before running the pipeline

Do NOT use CSV format - only Excel (.xlsx or .xls) files are supported

Column names are case-sensitive - use exactly: candidate_name, skills, email, notice_period_days

Accepted column name variations (auto-mapped):

Candidate Name → candidate_name

Skill or Skills → skills

Email ID or Email → email

Notice Period (Days) → notice_period_days

Skills Column Format:

Use comma-separated skills: Oracle Fusion, SQL, PLSQL, OIC

Multi-line text is supported and will be automatically cleaned

The matching algorithm uses text similarity on skills

Step 7: Verify Your Setup
powershell
# Check Python version
python --version

# Verify virtual environment is active
echo $env:VIRTUAL_ENV

# Test imports
python -c "import pandas; print('Pandas OK')"
python -c "import playwright; print('Playwright OK')"
Running the Pipeline
Important: Dry-Run vs Real Emails
By default, the pipeline runs in DRY-RUN mode - no emails are actually sent. You must explicitly add --send-emails to send real emails.

## Basic Commands
1. Dry Run (Test without sending emails)
powershell
python run_integrated_pipeline.py
2. Run with Custom Keyword
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 5
3. Send Real Emails (SMTP)
powershell
python run_integrated_pipeline.py --send-emails --email-provider smtp --notification-email recruiter@example.com
4. Send Real Emails (SendGrid)
powershell
python run_integrated_pipeline.py --send-emails --email-provider sendgrid --notification-email recruiter@example.com
## Advanced Commands
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
--max-age-hours	Ignore older jobs (hours)	24
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
naukri_browser_profile/	Playwright browser session data
Note about candidate_profiles.xlsx:

This is an INPUT file, not an output

You must create this file manually before running the pipeline

If the file doesn't exist, the pipeline will create an EMPTY template with column headers only

The pipeline will NOT populate this file with your candidate data

Email Dispatch Logic
When Emails Are Sent
Emails are only dispatched when ALL conditions are met:

✅ Valid candidate profiles loaded from Excel (file exists and has data)

✅ At least one candidate matches a job above the --min-score threshold

✅ --send-emails flag is provided

✅ Recipient email configured (via .env or --notification-email)

Email Filtering
The pipeline automatically filters to send emails ONLY for jobs that have matching candidates:

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
  "emails_dry_run": 0
}
If you do not see a message in inbox even when status=sent, check Spam/Promotions folder.

Troubleshooting Guide
Setup Issues
Issue	Solution
ModuleNotFoundError	Run pip install -r requirements.txt
Playwright browser missing	Run python -m playwright install chromium
Virtual environment not activating	Run Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Unicode/encoding errors	Set UTF-8 encoding (see above)
Candidate File Issues
Issue	Solution
File not found	Create output/candidate_profiles.xlsx manually
Empty template created	The pipeline creates empty template - you must add your data
Invalid file format	Use .xlsx or .xls only (no CSV files)
Missing columns	Add: candidate_name, skills, email, notice_period_days
No valid candidates	Ensure at least one row has name and skills (not empty)
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
Company name shows 'nan'	Fixed - defaults to "Client"
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

Create your candidate file BEFORE running - don't rely on auto-creation

Test with dry-run first (--send-emails not included)

Start with lower page count (--pages 1) for initial testing

Use heuristic/jaccard mode if adapter mode fails

Lower --min-score gradually from 0.12 → 0.08 → 0.05

Check shortlisted_profiles.csv before sending emails

Verify email configuration with a simple test script

Close Excel files before running the pipeline

Example Workflow
Step 1: Create Candidate Excel File
Create output/candidate_profiles.xlsx with your candidate data:

csv
candidate_name,skills,email,notice_period_days
John Doe,"Oracle Fusion, SQL, PLSQL",john@example.com,30
Jane Smith,"Oracle EBS, Fusion Financials, GL",jane@example.com,Immediate
Step 2: Initial Test (No Emails)
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 1 --rows 5
Step 3: Check Results
powershell
Import-Csv output\shortlisted_profiles.csv | Select-Object -First 10
Step 4: Adjust Threshold if Needed
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 3 --min-score 0.05
Step 5: Send Emails
powershell
python run_integrated_pipeline.py --keyword "Oracle Fusion" --pages 3 --min-score 0.05 --send-emails --notification-email recruiter@example.com
Step 6: Launch Dashboard
powershell
streamlit run src/dashboard/app.py
Support
If you encounter issues:

Check the troubleshooting guide above

Review output/pipeline_summary.json for warnings

Check output/email_dispatch.csv for email errors

Ensure candidate Excel file exists and has data (not just headers)

Verify all prerequisites are installed correctly

License
This project is open-source and available for use and modification.

