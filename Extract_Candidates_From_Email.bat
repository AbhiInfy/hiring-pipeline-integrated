@echo off
chcp 65001 > nul
title Email Candidate Extractor

echo ========================================
echo EMAIL CANDIDATE EXTRACTOR
echo ========================================
echo.

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

set /p hours="Scan emails from last N hours [24]: "
if "%hours%"=="" set hours=24

echo.
echo Scanning last %hours% hours of emails...
echo.

python -c "from src.email_extractor.candidate_extractor import extract_candidates_from_emails; extract_candidates_from_emails(hours_back=%hours%, max_emails=100)"

echo.
echo ========================================
echo Extraction completed!
echo Check output/candidate_profiles.xlsx
echo ========================================
pause