# PowerShell script for uninstalling browsermon on Windows

# Stop and remove the browsermon service
if (Get-Service -Name "browsermon" -ErrorAction SilentlyContinue) {
    Stop-Service "browsermon"
    Remove-Service "browsermon"
}

# Delete the installation directory
$TARGET_DIR = "C:\browsermon"
if (Test-Path $TARGET_DIR) {
    Remove-Item -Recurse -Force $TARGET_DIR
}

Write-Host "Uninstallation complete."

