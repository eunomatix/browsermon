#!/bin/bash

set -e

# Define the target directory
TARGET_DIR="/opt/browsermon"

# Function to echo a step and its description
echo_step() {
    echo "Step $1: $2"
}

# Function to stop and disable the systemd service
stop_and_disable_service() {
    echo_step 1 "Stopping and disabling the systemd service"
    SERVICE_NAME="browsermon.service"
    systemctl stop "$SERVICE_NAME" || echo "Failed to stop the service."
    systemctl disable "$SERVICE_NAME" || echo "Failed to disable the service."
}

# Function to remove the systemd service file
remove_service_file() {
    echo_step 2 "Removing the systemd service file"
    SYSTEMD_SYSTEM_DIR="/etc/systemd/system/"
    rm -f "$SYSTEMD_SYSTEM_DIR/browsermon.service" || echo "Failed to remove the service file."
}

# Function to delete the target directory
delete_target_directory() {
    echo_step 3 "Deleting the target directory"
    rm -rf "$TARGET_DIR" || echo "Failed to delete the target directory."
}

# Function to perform uninstallation steps
perform_uninstallation() {
    stop_and_disable_service
    remove_service_file
    delete_target_directory
    echo "Uninstallation complete."
}

# Main script
perform_uninstallation

