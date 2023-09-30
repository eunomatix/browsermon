/****************************************************************************
 **
 ** Copyright (C) 2023 EUNOMATIX
 ** This program is free software: you can redistribute it and/or modify
 ** it under the terms of the GNU General Public License as published by
 ** the Free Software Foundation, either version 3 of the License, or
 ** any later version.
 **
 ** This program is distributed in the hope that it will be useful,
 ** but WITHOUT ANY WARRANTY; without even the implied warranty of
 ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 ** GNU General Public License for more details.
 **
 ** You should have received a copy of the GNU General Public License
 ** along with this program. If not, see <https://www.gnu.org/licenses/>.
 **
 ** Contact: info@eunomatix.com
 **
 **************************************************************************/

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
