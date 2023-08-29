# PowerShell script for installing browsermon on Windows

# Check if running with administrative privileges
$isAdmin = ([System.Security.Principal.WindowsIdentity]::GetCurrent()).Groups -match "S-1-5-32-544"
if (-not $isAdmin) {
    Write-Host "Please run this script with administrative privileges."
    Read-Host "Press Enter to close this window..."
    Exit
}

# Define the target directory
$TARGET_DIR = "C:\browsermon"

# Create the target directory if it doesn't exist
if (-Not (Test-Path $TARGET_DIR)) {
    New-Item -ItemType Directory -Path $TARGET_DIR
}

# Copy browsermon files
Copy-Item browsermon.exe "$TARGET_DIR\"
Copy-Item README.md "$TARGET_DIR\"
Copy-Item browsermon.conf "$TARGET_DIR\"
Copy-Item win_uninstall.ps1 "$TARGET_DIR\"

# Install the browsermon service using the browsermon.exe install command
$browsermonExePath = Join-Path $TARGET_DIR "browsermon.exe"
Start-Process -FilePath $browsermonExePath -ArgumentList "--startup=auto install"

# Check if the service is installed and running
do {
    $serviceStatus = Get-Service -Name "browsermon" -ErrorAction SilentlyContinue
    if ($serviceStatus -ne $null) {
        # Start the browsermon service
        Start-Service "browsermon"
        Write-Host "Installation complete."
        break
    }
    Start-Sleep -Seconds 2
} while ($true)

# Wait for user input before closing the PowerShell window
Read-Host "Press Enter to close this window..."
