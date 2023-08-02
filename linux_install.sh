#!/bin/bash

# Exit immediately if any command exits with a non-zero status
set -e

# Function to check if a command is available
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to echo a step and its description
echo_step() {
    echo "Step $1: $2"
}

# Function to draw a progress bar
draw_progress_bar() {
    local percentage=$1
    local bar_length=50
    local num_bars=$(( percentage * bar_length / 100 ))

    # Print the progress bar
    printf "["
    for ((i=0; i<num_bars; i++)); do
        printf "="
    done
    for ((i=num_bars; i<bar_length; i++)); do
        printf " "
    done
    printf "] %d%%\r" $percentage
}

# Check if Python is installed
if ! command_exists python3; then
    echo "Error: Python is not installed. Please install Python 3 to proceed."
    exit 1
fi

# Check if pip is installed
if ! command_exists pip3; then
    echo "Error: pip is not installed. Please install pip for Python 3 to proceed."
    exit 1
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
    # Redirect output to /dev/null to hide the installation details
    if ! pip3 install -r "$REQUIREMENTS_FILE" >/dev/null 2>&1; then
        echo "Error: Failed to install dependencies."
        exit 1
    fi
}

# Function to delete the project directory
delete_project_directory() {
    echo_step 6 "Deleting the project directory"
    rm -rf "$PROJECT_DIR"
}

# Function to prompt the user for deleting the project directory
prompt_delete_project() {
    while true; do
        read -p "Do you want to delete the project directory? (y/n): " choice
        case "$choice" in
            [Yy]* )
                delete_project_directory
                break;;
            [Nn]* )
                echo "Project directory will not be deleted."
                break;;
            * )
                echo "Please enter 'y' for Yes or 'n' for No."
        esac
    done
}

# Function to perform installation steps with a progress bar
perform_installation() {
    total_steps=6
    step=0

    create_target_directory
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    copy_files
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    cp "$PROJECT_DIR/README.md" "$TARGET_DIR"
    cp "$PROJECT_DIR/browsermon.conf" "$TARGET_DIR"
    cp "$PROJECT_DIR/linux_uninstall.sh" "$TARGET_DIR"
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    install_dependencies
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    move_service_file
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    enable_and_start_service
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    prompt_delete_project
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))
    echo "Installation complete."
}

# Main script
perform_installation
