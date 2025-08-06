@echo off
echo Starting SPCA Foster Dashboard...
echo.
echo Make sure the CSV files are in the "__Load Files Go Here__" folder (parent directory):
echo - AnimalInventory.csv
echo - FosterCurrent.csv
echo.
pause
streamlit run foster_dashboard.py
pause 