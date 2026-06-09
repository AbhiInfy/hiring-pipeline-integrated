@echo off
setlocal

cd /d "%~dp0"

REM Set UTF-8 encoding for proper Unicode display
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run the pipeline with all arguments
python "run_integrated_pipeline.py" %*

endlocal