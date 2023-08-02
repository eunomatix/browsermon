#!/bin/bash

# Define the target directory
TARGET_DIR="/opt/browsermon"

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

# Function to stop and disable the systemd service
stop_and_disable_service() {
    echo_step 1 "Stopping and disabling the systemd service"
    SERVICE_NAME="browsermon.service"
    systemctl stop "$SERVICE_NAME"
    systemctl disable "$SERVICE_NAME"
}

# Function to remove the systemd service file
remove_service_file() {
    echo_step 2 "Removing the systemd service file"
    SYSTEMD_SYSTEM_DIR="/etc/systemd/system/"
    rm -f "$SYSTEMD_SYSTEM_DIR/browsermon.service"
}

# Function to delete the target directory
delete_target_directory() {
    echo_step 3 "Deleting the target directory"
    rm -rf "$TARGET_DIR"
}

# Function to perform uninstallation steps with a progress bar
perform_uninstallation() {
    total_steps=3
    step=0

    stop_and_disable_service
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    remove_service_file
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))

    delete_target_directory
    ((step++))
    draw_progress_bar $((step * 100 / total_steps))
    echo "Uninstallation complete."
}

# Main script
perform_uninstallation

