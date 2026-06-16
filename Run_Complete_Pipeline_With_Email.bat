@echo off
chcp 65001 > nul
title Complete Hiring Pipeline with Email Extraction

echo ========================================
echo COMPLETE HIRING PIPELINE
echo ========================================
echo This will:
echo 1. Extract candidates from emails
echo 2. Scrape jobs from Naukri
echo 3. Match candidates to jobs
echo 4. Send shortlist emails
echo.

set /p keyword="Enter technology [Oracle Fusion Application]: "
if "%keyword%"=="" set keyword=Oracle Fusion Application

set /p pages="Enter pages to scan [3]: "
if "%pages%"=="" set pages=3

set /p hours="Scan emails from last N hours [24]: "
if "%hours%"=="" set hours=24

echo.
echo Running with:
echo   Technology: %keyword%
echo   Pages: %pages%
echo   Email scan: Last %hours% hours
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python run_integrated_pipeline.py --extract-from-emails --email-hours %hours% --max-emails 100 --keyword "%keyword%" --pages %pages% --min-score 0.12 --top-k 5 --send-emails --notification-email chaturvedi.abhishek10@gmail.com

echo.
echo ========================================
echo PIPELINE COMPLETED
echo ========================================
echo Check these files:
echo   - output/candidate_profiles.xlsx (extracted candidates)
echo   - output/shortlisted_profiles.csv (matches)
echo   - output/email_dispatch.csv (email log)
echo.
pause