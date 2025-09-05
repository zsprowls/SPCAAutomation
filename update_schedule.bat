@echo off
echo Updating PetPoint automation schedule to business hours...
echo ========================================================

REM Run the PowerShell script to update the schedule
powershell.exe -ExecutionPolicy Bypass -File "update_schedule_business_hours.ps1"

echo.
echo Schedule update completed!
pause