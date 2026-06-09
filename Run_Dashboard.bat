@echo off
setlocal

cd /d "%~dp0"

REM Set UTF-8 encoding
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

echo ============================================================
echo Launching Hiring Pipeline Dashboard
echo ============================================================
echo.

REM Check if output files exist
if not exist "output\shortlisted_profiles.csv" (
    echo [WARNING] No pipeline output found!
    echo Please run Run_Integrated_Pipeline.bat first to generate data.
    echo.
)

REM Try to use virtual environment Python first
set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if exist "%PYTHON_EXE%" (
    echo Using virtual environment...
    "%PYTHON_EXE%" -m streamlit run "src\dashboard\app.py"
) else (
    echo Using system Python...
    python -m streamlit run "src\dashboard\app.py"
)

endlocal
