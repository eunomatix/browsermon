# PowerShell script for uninstalling browsermon on Windows

# Check if the script is running from the target directory
$TARGET_DIR = "C:\browsermon"
$scriptPath = $MyInvocation.MyCommand.Path
$scriptDirectory = Split-Path -Parent $scriptPath

if ($scriptDirectory -eq $TARGET_DIR) {
    Write-Host "Please move this script to a different directory before running it."
    Write-Host "The target directory ($TARGET_DIR) is in use and can't be deleted."
    Exit
}

# Stop the browsermon service if it's running
if (Get-Service -Name "browsermon" -ErrorAction SilentlyContinue) {
    Stop-Service "browsermon"
}

# Wait for the service to stop
do {
    $serviceStatus = Get-Service -Name "browsermon" -ErrorAction SilentlyContinue
    if ($serviceStatus -eq $null -or $serviceStatus.Status -eq "Stopped") {
        break
    }
    Start-Sleep -Seconds 2
} while ($true)

# Remove the browsermon service using the browsermon.exe remove command
$browsermonExePath = Join-Path $TARGET_DIR "browsermon.exe"
Start-Process -FilePath $browsermonExePath -ArgumentList "remove"

# Wait for the service to be removed
do {
    $serviceStatus = Get-Service -Name "browsermon" -ErrorAction SilentlyContinue
    if ($serviceStatus -eq $null) {
        break
    }
    Start-Sleep -Seconds 2
} while ($true)

# Wait until the browsermon.exe process is not running before deleting the file
do {
    $browsermonProcess = Get-Process -Name "browsermon" -ErrorAction SilentlyContinue
    if ($browsermonProcess -eq $null) {
        break
    }
    Start-Sleep -Seconds 2
} while ($true)

# Forcefully delete the browsermon.exe file
$browsermonExePath = Join-Path $TARGET_DIR "browsermon.exe"
Remove-Item -Path $browsermonExePath -Force -ErrorAction SilentlyContinue

# Delete the installation directory
if (Test-Path $TARGET_DIR) {
    Remove-Item -Recurse -Force $TARGET_DIR
}

Write-Host "Uninstallation complete."
