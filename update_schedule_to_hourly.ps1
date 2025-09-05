# PowerShell script to update the PetPoint automation schedule from 15 minutes to hourly
# This helps prevent IP blocking by reducing the frequency of requests

Write-Host "Updating PetPoint automation schedule to run hourly instead of every 15 minutes..." -ForegroundColor Green

try {
    # Check if the task exists
    $taskName = "PetPoint Automation"
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if ($task) {
        Write-Host "Found existing task: $taskName" -ForegroundColor Yellow
        
        # Update the trigger to run hourly from 5:55 AM to 6:55 PM
        $startTime = Get-Date "5:55 AM"
        $endTime = Get-Date "6:55 PM"
        $trigger = New-ScheduledTaskTrigger -Once -At $startTime -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Hours 13)
        
        # Get the current task settings
        $settings = $task.Settings
        
        # Update the task with the new trigger
        Set-ScheduledTask -TaskName $taskName -Trigger $trigger -Settings $settings
        
        Write-Host "✅ Successfully updated task to run hourly!" -ForegroundColor Green
        Write-Host "The task will now run every hour instead of every 15 minutes." -ForegroundColor Cyan
        Write-Host "This should help prevent IP blocking issues." -ForegroundColor Cyan
        
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
            if ($trigger.Repetition) {
                Write-Host "Repetition Interval: $($trigger.Repetition.Interval)"
                Write-Host "Repetition Duration: $($trigger.Repetition.Duration)"
            }
        }
        
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
