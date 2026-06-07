@echo off
setlocal

cd /d "%~dp0"
python "run_integrated_pipeline.py" %*

endlocal
