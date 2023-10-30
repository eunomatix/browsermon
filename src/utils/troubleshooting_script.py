import os
import json
import shutil

# Define the output directory for the JSON files
OUTPUT_DIR = "/opt/browsermon/troubleshootingfiles"

# Check if the output directory exists, create it if not
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# List all users on the system
USERS = [entry.name for entry in os.scandir("/home") if entry.is_dir()]

# Loop through each user
for USER in USERS:
    HOME_DIR = os.path.join("/home", USER)

    # Check if the "Local State" file exists in the user's home folder
    LOCAL_STATE_FILE = os.path.join(HOME_DIR, ".config/microsoft-edge/Local State")

    if os.path.isfile(LOCAL_STATE_FILE):
        # Extract profile information and save it as a JSON file
        with open(LOCAL_STATE_FILE, "r") as file:
            data = json.load(file)
            profile_info = data.get("profile", {}).get("info_cache", {})

        PROFILES_JSON = os.path.join(OUTPUT_DIR, f"profiles_{USER}.json")

        with open(PROFILES_JSON, "w") as json_file:
            json.dump(profile_info, json_file, indent=4)

print("Profile extraction complete. JSON files are available in", OUTPUT_DIR)

# Copy browsermon.conf and browsermon.log files from /opt/browsermon/
BROWSERMON_DIR = "/opt/browsermon"
CONF_FILE = os.path.join(BROWSERMON_DIR, "../../browsermon.conf")
LOG_FILE = os.path.join(BROWSERMON_DIR, "browsermon.log")

if os.path.exists(CONF_FILE):
    shutil.copy(CONF_FILE, OUTPUT_DIR)

if os.path.exists(LOG_FILE):
    shutil.copy(LOG_FILE, OUTPUT_DIR)

print("browsermon.conf and browsermon.log files copied to", OUTPUT_DIR)
