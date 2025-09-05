# PowerShell script to update the PetPoint automation schedule to run hourly during business hours
# This helps prevent IP blocking by running only during business hours (5:55 AM - 6:55 PM)

Write-Host "Updating PetPoint automation schedule to run hourly during business hours (5:55 AM - 6:55 PM)..." -ForegroundColor Green

try {
    # Check if the task exists
    $taskName = "PetPoint Automation"
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($task) {
        Write-Host "Found existing task: $taskName" -ForegroundColor Yellow
        
        # Create a daily trigger that runs every hour from 5:55 AM to 6:55 PM
        $trigger = New-ScheduledTaskTrigger -Daily -At "5:55 AM"
        $trigger.Repetition.Interval = "PT1H"  # Every 1 hour
        $trigger.Repetition.Duration = "PT13H"  # For 13 hours (5:55 AM to 6:55 PM)
        
        # Get the current task settings
        $settings = $task.Settings
        
        # Update the task with the new trigger
        Set-ScheduledTask -TaskName $taskName -Trigger $trigger -Settings $settings
        
        Write-Host "✅ Successfully updated task to run hourly during business hours!" -ForegroundColor Green
        Write-Host "The task will now run every hour from 5:55 AM to 6:55 PM (13 runs per day)." -ForegroundColor Cyan
        Write-Host "This is much safer than every 15 minutes (96 runs per day)." -ForegroundColor Cyan
        
        # Show the updated task info
        $updatedTask = Get-ScheduledTask -TaskName $taskName
        Write-Host "`nUpdated task details:" -ForegroundColor Yellow
        Write-Host "Task Name: $($updatedTask.TaskName)"
        Write-Host "State: $($updatedTask.State)"
        Write-Host "Next Run Time: $($updatedTask.NextRunTime)"
        
        # Show trigger details
        $triggers = $updatedTask.Triggers
        foreach ($trigger in $triggers) {
            Write-Host "Trigger Type: $($trigger.CimClass.CimClassName)"
            Write-Host "Start Time: $($trigger.StartBoundary)"
            if ($trigger.Repetition) {
                Write-Host "Repetition Interval: $($trigger.Repetition.Interval)"
                Write-Host "Repetition Duration: $($trigger.Repetition.Duration)"
            }
        }
        
        Write-Host "`n📊 Schedule Summary:" -ForegroundColor Green
        Write-Host "• Runs: 13 times per day (vs 96 times with 15-minute schedule)" -ForegroundColor White
        Write-Host "• Hours: 5:55 AM - 6:55 PM (business hours)" -ForegroundColor White
        Write-Host "• Frequency: Every hour" -ForegroundColor White
        Write-Host "• Risk: Much lower chance of IP blocking" -ForegroundColor White
        
    } else {
        Write-Host "❌ Task '$taskName' not found!" -ForegroundColor Red
        Write-Host "Available tasks:" -ForegroundColor Yellow
        Get-ScheduledTask | Where-Object {$_.TaskName -like "*PetPoint*" -or $_.TaskName -like "*petpoint*"} | ForEach-Object {
            Write-Host "  - $($_.TaskName)" -ForegroundColor Cyan
        }
        Write-Host "`nPlease check the task name and try again." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error updating scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "You may need to run this script as Administrator." -ForegroundColor Yellow
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

