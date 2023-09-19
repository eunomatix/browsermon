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

#!/bin/bash

set -e

# Check if the user is root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root."
    exit 1
fi

# Function to check if a command is available
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to echo a step and its description
echo_step() {
    echo "Step $1: $2"
}

# Install Python and pip if not installed
if ! command_exists python3 || ! command_exists pip3; then
    if command_exists apt-get; then
        apt-get update
        apt-get install -y python3 python3-pip
    elif command_exists yum; then
        yum install -y python3 python3-pip
    elif command_exists dnf; then
        dnf install -y python3 python3-pip
    elif command_exists zypper; then
        zypper install -y python3 python3-pip
    elif command_exists pacman; then
        pacman -S --noconfirm python python-pip
    else
        echo "Error: Unsupported Linux distribution. Please install Python and pip manually."
        exit 1
    fi
fi

# Get the current directory
PROJECT_DIR=$(pwd)

# Define the target directory
TARGET_DIR="/opt/browsermon"

# Function to create the target directory if it doesn't exist
create_target_directory() {
    echo_step 1 "Creating target directory"
    if [ ! -d "$TARGET_DIR" ]; then
        mkdir -p "$TARGET_DIR"
    fi
}

# Function to copy files from source directory to the target directory
copy_files() {
    echo_step 2 "Copying files to the target directory"
    SRC_DIR="$PROJECT_DIR/src"
    cp -r "$SRC_DIR" "$TARGET_DIR"/
}

# Function to move the systemd service file to the system-wide services directory
move_service_file() {
    echo_step 3 "Moving systemd service file"
    SYSTEMD_SERVICE_FILE="$PROJECT_DIR/service/browsermon.service"
    SYSTEMD_SYSTEM_DIR="/etc/systemd/system/"
    cp "$SYSTEMD_SERVICE_FILE" "$SYSTEMD_SYSTEM_DIR"
}

# Function to enable and start the systemd service
enable_and_start_service() {
    echo_step 4 "Enabling and starting the systemd service"
    SERVICE_NAME="browsermon.service"
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
}

# Function to install required Python dependencies from requirements.txt
install_dependencies() {
    echo_step 5 "Installing Python dependencies"
    REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

    # Check Python version
    PYTHON_VERSION=$(python3 -c "import sys; print('{}.{}'.format(sys.version_info.major, sys.version_info.minor))")

    # Compare Python version using bash comparison
    if [[ "$PYTHON_VERSION" == 3.* ]]; then
        MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        if (( MAJOR >= 3 && MINOR >= 3 )); then
            # Create and activate a virtual environment
            python3 -m venv "$TARGET_DIR/venv"
            source "$TARGET_DIR/venv/bin/activate"

            # Install dependencies using pip
            if ! pip install -r "$REQUIREMENTS_FILE"; then
                echo "Error: Failed to install dependencies."
                deactivate
                exit 1
            fi

            # Deactivate the virtual environment
            deactivate
        else
            echo "Error: Python 3.3 or newer is required. Please install a compatible version."
            exit 1
        fi
    else
        echo "Error: Python 3.3 or newer is required. Please install a compatible version."
        exit 1
    fi
}

# Main script
create_target_directory
#copy_files
cp "$PROJECT_DIR/browsermon" "$TARGET_DIR"
cp "$PROJECT_DIR/README.md" "$TARGET_DIR"
cp "$PROJECT_DIR/browsermon.conf" "$TARGET_DIR"
cp "$PROJECT_DIR/linux_uninstall.sh" "$TARGET_DIR"

#install_dependencies

move_service_file

enable_and_start_service

echo "Installation complete."

