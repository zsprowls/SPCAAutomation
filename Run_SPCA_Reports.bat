@echo off
echo ========================================
echo    SPCA Reports Automation Tool
echo ========================================
echo.
echo This will run the SPCA reports in sequence:
echo 1. Clear File Processing
echo 2. Morning Email Report
echo.
echo Make sure you have updated the files in:
echo "__Load Files Go Here__" folder
echo.
pause

echo.
echo ========================================
echo Step 1: Running Clear File Processing...
echo ========================================
python "SPCA_Rounds\clear_file.py"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Clear file processing failed!
    echo Please check that the files in "__Load Files Go Here__" are up to date.
    pause
    exit /b 1
)
echo ✅ Clear file processing completed successfully!

echo.
echo ========================================
echo Step 2: Running Morning Email Report...
echo ========================================
python "MorningEmail\morning_email.py"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Morning email report failed!
    echo Please check that the files in "__Load Files Go Here__" are up to date.
    pause
    exit /b 1
)
echo ✅ Morning email report completed successfully!

echo.
echo ========================================
echo 🎉 All reports completed successfully!
echo ========================================
echo.
echo Check the following locations for output files:
echo - SPCA_Rounds\clear.csv
echo - MorningEmail\morning_email.docx
echo.
pause 