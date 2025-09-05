# PowerShell script to create a NEW PetPoint automation scheduled task
# This will run hourly during business hours (5:55 AM - 6:55 PM)

Write-Host "Creating NEW PetPoint automation scheduled task..." -ForegroundColor Green

try {
    # Task configuration
    $taskName = "PetPoint Automation"
    $taskDescription = "Automatically downloads PetPoint reports every hour during business hours"
    $scriptPath = Join-Path $PSScriptRoot "run_3_reports.bat"
    
    Write-Host "Script path: $scriptPath" -ForegroundColor Cyan
    
    # Check if the script exists
    if (-not (Test-Path $scriptPath)) {
        Write-Host "❌ Error: run_3_reports.bat not found at $scriptPath" -ForegroundColor Red
        Write-Host "Please make sure you're running this from the correct directory." -ForegroundColor Yellow
        exit 1
    }
    
    # Check if task already exists
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "⚠️  Task '$taskName' already exists!" -ForegroundColor Yellow
        Write-Host "Current state: $($existingTask.State)" -ForegroundColor Cyan
        $response = Read-Host "Do you want to delete and recreate it? (y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            Write-Host "Deleting existing task..." -ForegroundColor Yellow
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        } else {
            Write-Host "Cancelled. Exiting." -ForegroundColor Yellow
            exit 0
        }
    }
    
    # Create the action (what to run)
    $action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $PSScriptRoot
    
    # Create the trigger (when to run - daily at 5:55 AM, repeat every hour for 13 hours)
    $trigger = New-ScheduledTaskTrigger -Daily -At "5:55 AM"
    $trigger.Repetition.Interval = "PT1H"  # Every 1 hour
    $trigger.Repetition.Duration = "PT13H"  # For 13 hours (5:55 AM to 6:55 PM)
    
    # Create task settings
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
    
    # Create the principal (run as current user)
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType InteractiveToken
    
    # Register the scheduled task
    Write-Host "Creating scheduled task..." -ForegroundColor Yellow
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $taskDescription
    
    Write-Host "✅ Successfully created scheduled task!" -ForegroundColor Green
    Write-Host "`nTask Details:" -ForegroundColor Yellow
    Write-Host "• Name: $taskName" -ForegroundColor White
    Write-Host "• Description: $taskDescription" -ForegroundColor White
    Write-Host "• Script: $scriptPath" -ForegroundColor White
    Write-Host "• Schedule: Daily at 5:55 AM, repeat every hour for 13 hours" -ForegroundColor White
    Write-Host "• Runs: 5:55 AM, 6:55 AM, 7:55 AM, ..., 6:55 PM (13 times total)" -ForegroundColor White
    
    # Show the task info
    $newTask = Get-ScheduledTask -TaskName $taskName
    Write-Host "`nTask Status:" -ForegroundColor Yellow
    Write-Host "• State: $($newTask.State)" -ForegroundColor White
    Write-Host "• Next Run Time: $($newTask.NextRunTime)" -ForegroundColor White
    
    Write-Host "`n📊 Schedule Summary:" -ForegroundColor Green
    Write-Host "• Runs: 13 times per day (vs 96 times with 15-minute schedule)" -ForegroundColor White
    Write-Host "• Hours: 5:55 AM - 6:55 PM (business hours)" -ForegroundColor White
    Write-Host "• Frequency: Every hour" -ForegroundColor White
    Write-Host "• Risk: Much lower chance of IP blocking" -ForegroundColor White
    
    Write-Host "`n🎉 Task created successfully! It will start running tomorrow at 5:55 AM." -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error creating scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "You may need to run this script as Administrator." -ForegroundColor Yellow
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
