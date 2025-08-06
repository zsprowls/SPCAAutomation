@echo off
echo 🐹 Generating Rodent Status Report...
echo.

cd /d "%~dp0"
python rodent_spreadsheet_generator.py

echo.
echo ✅ Report generation complete!
pause 