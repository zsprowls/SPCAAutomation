# PowerShell script to set up Windows Task Scheduler for PetPoint automation
# Run this as Administrator

Write-Host "Setting up PetPoint Automation Task Scheduler..." -ForegroundColor Green

# Get the current directory
$scriptPath = Get-Location
$batchFile = Join-Path $scriptPath "run_petpoint_automation.bat"

Write-Host "Script path: $batchFile" -ForegroundColor Yellow

# Create the scheduled task
$action = New-ScheduledTaskAction -Execute $batchFile
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 15) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Register the task
Register-ScheduledTask -TaskName "PetPoint Automation" -Action $action -Trigger $trigger -Settings $settings -Description "Automatically exports PetPoint reports every 15 minutes"

Write-Host "✅ Task created successfully!" -ForegroundColor Green
Write-Host "Task Name: PetPoint Automation" -ForegroundColor Cyan
Write-Host "Frequency: Every 15 minutes" -ForegroundColor Cyan
Write-Host "Logs will be saved to: __Load Files Go Here__/AutomationLog/" -ForegroundColor Cyan

Write-Host "`nTo manage this task:" -ForegroundColor Yellow
Write-Host "1. Open Task Scheduler (taskschd.msc)" -ForegroundColor White
Write-Host "2. Look for 'PetPoint Automation' in the Task Scheduler Library" -ForegroundColor White
Write-Host "3. You can enable/disable, modify schedule, or view history there" -ForegroundColor White

Write-Host "`nTo run the task manually for testing:" -ForegroundColor Yellow
Write-Host "Run: $batchFile" -ForegroundColor White
