# Simple script to create PetPoint automation task
Write-Host "Creating PetPoint Automation task..." -ForegroundColor Green

try {
    # Get current directory
    $currentDir = Get-Location
    $scriptPath = Join-Path $currentDir "run_3_reports.bat"
    
    Write-Host "Current directory: $currentDir" -ForegroundColor Cyan
    Write-Host "Script path: $scriptPath" -ForegroundColor Cyan
    
    # Check if script exists
    if (Test-Path $scriptPath) {
        Write-Host "✅ Script found!" -ForegroundColor Green
    } else {
        Write-Host "❌ Script not found!" -ForegroundColor Red
        exit 1
    }
    
    # Create the task action
    $action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $currentDir
    
    # Create daily trigger at 5:55 AM with hourly repetition for 13 hours
    $trigger = New-ScheduledTaskTrigger -Daily -At "5:55 AM"
    $trigger.Repetition.Interval = "PT1H"  # Every 1 hour
    $trigger.Repetition.Duration = "PT13H"  # For 13 hours (5:55 AM to 6:55 PM)
    
    # Create task settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    
    # Create principal
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive
    
    # Register the task
    Write-Host "Registering task..." -ForegroundColor Yellow
    Register-ScheduledTask -TaskName "PetPoint Automation" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Downloads PetPoint reports daily at 5:55 AM"
    
    Write-Host "✅ Task created successfully!" -ForegroundColor Green
    
    # Verify it was created
    $task = Get-ScheduledTask -TaskName "PetPoint Automation" -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "✅ Task verified in Task Scheduler!" -ForegroundColor Green
        Write-Host "Task Name: $($task.TaskName)" -ForegroundColor White
        Write-Host "State: $($task.State)" -ForegroundColor White
        Write-Host "Next Run: $($task.NextRunTime)" -ForegroundColor White
    } else {
        Write-Host "❌ Task not found after creation!" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Full error: $($_.Exception)" -ForegroundColor Red
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
Read-Host
