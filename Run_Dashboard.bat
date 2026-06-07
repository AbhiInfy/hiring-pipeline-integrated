@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
if exist "%PYTHON_EXE%" (
	"%PYTHON_EXE%" -m streamlit run "src\dashboard\app.py"
) else (
	python -m streamlit run "src\dashboard\app.py"
)

endlocal
