@echo off
echo Creating NEW PetPoint automation scheduled task...
echo =================================================

REM Run the PowerShell script to create the new scheduled task
powershell.exe -ExecutionPolicy Bypass -File "create_new_scheduled_task.ps1"

echo.
echo Task creation completed!
pause

