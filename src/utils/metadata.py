import os
import platform
import sqlite3

from utils import system


def get_browser_version(user_profile_dir, browser_name):
    """
    Return the latest browser version by reading the version file of the
    specified browser.
    :param user_profile_dir: User profile directory
    :param browser_name: Name of the browser (e.g., "Edge", "Firefox",
    etc.) :return: Latest browser version
    """
    version = ""
    version_file_path = None

    if browser_name.lower() == "edge":
        version_file_path = os.path.join(user_profile_dir, "..",
                                         "Last Version")
    elif browser_name.lower() == "firefox":
        version_file_path = os.path.join(user_profile_dir, "compatibility.ini")

    if version_file_path and os.path.exists(version_file_path):
        with open(version_file_path, "r") as file:
            version_data = file.read()
            if browser_name.lower() == "edge":
                version = version_data.strip()
            elif browser_name.lower() == "firefox":
                for line in version_data.splitlines():
                    if line.startswith("LastVersion="):
                        version = line.split("LastVersion=")[-1].strip()
                        break

    return version


def get_static_metadata(user_profile_dir, username, browser_name):
    """
    Get the static metadata for the browser and system.
    :return: Static metadata dictionary
    """

    metadata = {"hostname": platform.node(), "os": system,
                "os_username": username, "browser": browser_name,
                "browser_version": get_browser_version(user_profile_dir,
                                                       browser_name),
                "browser_db": f"SQLite {sqlite3.sqlite_version}"}
    return metadata
