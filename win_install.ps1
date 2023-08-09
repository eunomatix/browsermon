# PowerShell script for installing browsermon on Windows

# Define the target directory
$TARGET_DIR = "C:\browsermon"

# Check if Python is installed
$pythonExe = Get-Command python.exe -ErrorAction SilentlyContinue
if ($pythonExe -eq $null) {
    Write-Host "Error: Python is not installed. Please install Python to proceed."
    exit 1
}

# Check if pip is installed
$pipExe = Get-Command pip.exe -ErrorAction SilentlyContinue
if ($pipExe -eq $null) {
    Write-Host "Error: pip is not installed. Please install pip to proceed."
    exit 1
}

# Get Python version
$pythonVersion = & $pythonExe --version 2>&1
if ($pythonVersion -match 'Python (\d+\.\d+)') {
    $pythonVersionNumber = $Matches[1]
    if ([version]$pythonVersionNumber -lt [version]'3.6') {
        Write-Host "Error: Python 3.6 or newer is required. Please install a compatible version."
        exit 1
    }
} else {
    Write-Host "Error: Failed to determine Python version."
    exit 1
}

# Create the target directory if it doesn't exist
if (-Not (Test-Path $TARGET_DIR)) {
    New-Item -ItemType Directory -Path $TARGET_DIR
}

# Copy files from source directory to the target directory
Copy-Item -Recurse -Force "src\*" $TARGET_DIR

# Copy additional files
Copy-Item README.md "$TARGET_DIR\"
Copy-Item browsermon.conf "$TARGET_DIR\"
Copy-Item windows_uninstall.ps1 "$TARGET_DIR\"

# Install required Python dependencies from requirements.txt
pip install -r requirements.txt

# Register the browsermon service as a Windows service
New-Service -Name "browsermon" -BinaryPathName "$TARGET_DIR\controller.py" -DisplayName "browsermon Service"

# Start the service
Start-Service "browsermon"

Write-Host "Installation complete."

