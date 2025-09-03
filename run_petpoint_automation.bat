@echo off
echo Starting PetPoint Automation...
echo ================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Activate virtual environment
call petpoint_env\Scripts\activate.bat

REM Run the automation script
python petpoint_export_3_reports.py

echo Automation completed at %date% %time%
