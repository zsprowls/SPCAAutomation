@echo off
echo Running PetPoint Export - 3 Reports Only
echo =========================================

REM Change to the directory where this batch file is located
cd /d "%~dp0"

REM Activate virtual environment
call petpoint_env\Scripts\activate.bat

REM Run the 3 reports script
python petpoint_export_3_reports.py

echo.
echo Export completed! Check the "__Load Files Go Here__" folder for your files.
pause
