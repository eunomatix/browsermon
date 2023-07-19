import atexit
import base64
import ctypes
import datetime
import hashlib
import json
import logging
import os
import platform
import sqlite3
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from cryptography.fernet import Fernet


def write_logs(level, message):
    """
    Write logs to the browsermon.log file
    :param level: Log level (info, error, warning)
    :param message: Log message
    :return: None
    """
    log_file = os.path.join(loggingdir, "browsermon.log")
    log_format = "%(asctime)s WD%(process)d:: \'MICROSOFT-EDGE:\' - %(levelname)s %(message)s"  # noqa
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format=log_format)

    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    elif level == "warning" or level == "warn":
        logging.warning(message)


def get_browser_version(user_profile_dir):
    """
    Return the latest browser version by reading the Last Version file.
    :param user_profile_dir: User profile directory
    :return: Latest browser version
    """
    version = ""
    last_version_file = os.path.join(user_profile_dir, "..",
                                     "Last Version")
    if os.path.exists(last_version_file):
        with open(last_version_file, "r") as file:
            version = file.read().strip()
    return version


def get_static_metadata(user_profile_dir, username):
    """
    Get the static metadata for the browser and system.
    :return: Static metadata dictionary
    """
    metadata = {
        "hostname": platform.node(),
        "os": system,
        "os_username": username,
        "browser": "Microsoft Edge",
        "browser_version": get_browser_version(user_profile_dir),
        "browser_db": f"SQLite {sqlite3.sqlite_version}"
    }
    return metadata


def get_profiles(user_profile_dir, username):
    """
    Get the profiles from the Local State file.
    :return: Dictionary of profiles
    """
    write_logs("info",
               f"Sniffing user profiles from user: {username}")
    local_state_file = os.path.join(user_profile_dir, "Local State")
    with open(local_state_file, "r") as file:
        data = json.load(file)

    profile_info = data.get("profile")
    profiles = {}
    if profile_info and "info_cache" in profile_info:
        profiles = {
            profile_name: {
                "profile_title": user_data.get("name"),
                "profile_username": user_data.get("user_name"),
                "profile_path": os.path.join(user_profile_dir,
                                             profile_name),
                "username": username,
            }
            for profile_name, user_data in
            profile_info["info_cache"].items()
        }

    return profiles


def get_all_profiles():
    """
    Get all the profiles for all the users on the operating system.
    :return: Dictionary of profiles
    """
    write_logs("info", f"Sniffing users from {platform.node()}")
    profiles = {}

    if system == "Windows":
        import winreg

        try:
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                sid = winreg.EnumKey(reg_key, i)
                user_key = winreg.OpenKey(reg_key, sid)
                try:
                    profile_dir, _ = winreg.QueryValueEx(user_key, "ProfileImagePath")
                    username = os.path.basename(profile_dir)
                    user_profile_dir = os.path.join(profile_dir, "AppData",
                                                    "Local", "Microsoft", "Edge",
                                                    "User Data")
                    if os.path.exists(user_profile_dir):
                        write_logs("info",
                                   f"Found Microsoft Edge profile directory for user: {username}") #noqa
                        user_profiles = get_profiles(user_profile_dir, username)
                        profiles.update(user_profiles)
                finally:
                    winreg.CloseKey(user_key)
        finally:
            winreg.CloseKey(reg_key)
    else:  # Assume Linux
        for user in os.listdir('/home'):
            user_profile_dir = os.path.join('/home', user, '.config',
                                            'microsoft-edge')

            # Check if the user has a Microsoft Edge profile directory
            if os.path.exists(user_profile_dir):
                write_logs("info",
                           f"Found Microsoft Edge profile directory for user: {user}")
                user_profiles = get_profiles(user_profile_dir, user)
                profiles.update(user_profiles)

    return profiles


def write_history_data_to_json(profile):
    """
    Write the browsing history data for a given profile to the JSON file.
    :param profile: Profile information
    :return: None
    """
    metadata = get_static_metadata(profile["profile_path"],
                                   profile["username"])

    history_file = os.path.join(profile["profile_path"], "History")

    connection = sqlite3.connect(f"file:{history_file}?immutable=1",
                                 uri=True)
    cursor = connection.cursor()

    # SQLite query to retrieve the data
    query = """
        SELECT
            ca.window_id AS session_id,
            u_referrer.url AS referrer,
            u.url,
            u.title,
            v.visit_time,
            u.visit_count
        FROM
            Context_annotations AS ca
            INNER JOIN Visits AS v ON ca.visit_id = v.id
            INNER JOIN URLs AS u ON u.id = v.url
            LEFT JOIN Visits AS v_referrer ON v.from_visit = v_referrer.id
            LEFT JOIN URLs AS u_referrer ON v_referrer.url = u_referrer.id
        """

    last_visit_time = last_visit_times.get(
        profile["profile_title"])  # Get the last visit time for the profile

    if last_visit_time:
        # Filter for new records based on last processed visit time
        query += " WHERE v.visit_time > ?"
        cursor.execute(query, (last_visit_time,))
    else:
        cursor.execute(query)
    rows = cursor.fetchall()

    with open(output_file, "a+") as file:

        num_new_records = len(
            rows)  # Count the number of new records found
        write_logs("info",
                   f"Found {num_new_records} new records for profile '{profile['profile_title']}' user: '{profile['username']}'")  # noqa

        for result in rows:
            session_id = result[0]
            referrer = result[1]
            url = result[2]
            title = result[3]
            visit_time = result[4]
            visit_count = result[5]

            visit_time_obj = datetime.datetime(1601, 1,
                                               1) + datetime.timedelta(
                microseconds=visit_time)
            visit_time_str = visit_time_obj.strftime(
                "%Y-%m-%d %H:%M:%S")

            entry = {}

            entry.update(metadata)
            entry.update(profile)
            # Create a dictionary for each row of data
            entry.update({
                "session_id": session_id,
                "referrer": referrer,
                "url": url,
                "title": title,
                "visit_time": visit_time_str,
                "visit_count": visit_count
            })

            file.write(json.dumps(entry, indent=4))
            file.write(",\n")

        if rows:
            # Update the last processed visit time to the latest record's visit time
            last_visit_times[profile["profile_title"]] = rows[-1][4]

    cursor.close()
    connection.close()

    write_logs("info",
               f"Processed browsing history for profile '{profile['profile_title']}'")


def process_edge_history():
    """
    Process the Edge browsing history and write it to the output file.
    :return: None
    """
    profiles = get_all_profiles()

    for profile in profiles.values():
        write_history_data_to_json(profile)

    write_logs("info",
               "Processed browsing history for all the profiles and users")


class InvalidScheduleWindowFormat(Exception):
    """
    Custom exception for the InvalidScheduleWindowFormat
    """
    pass


def parse_schedule_window(window):
    """
    Parse the schedule window argument into seconds.
    :param window: Schedule window argument (e.g., 1m, 1h, 1d)
    :return: Schedule window in seconds
    """
    try:
        if window[-1] == "m":
            return int(window[:-1]) * 60
        elif window[-1] == "h":
            return int(window[:-1]) * 3600
        elif window[-1] == "d":
            return int(window[:-1]) * 86400
        else:
            raise InvalidScheduleWindowFormat
    except InvalidScheduleWindowFormat:
        print(
            "Invalid schedule window format. Please use the valid format (e.g., 1m, 1h, 1d)")  # noqa
        sys.exit(1)


def gen_fernet_key(passcode: bytes) -> bytes:
    assert isinstance(passcode, bytes)
    hlib = hashlib.md5()
    hlib.update(passcode)
    return base64.urlsafe_b64encode(hlib.hexdigest().encode('latin-1'))


def encrypt_data(data, key):
    """
    Encrypt the data using AES encryption with the key.
    :param data: Data to be encrypted
    :param key: Encryption key
    :return: Encrypted data
    """
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data


def decrypt_data(data, key):
    """
    Decrypt the data using AES encryption with the key.
    :param data: Data to be decrypted
    :param key: Decryption key
    :return: Decrypted data
    """
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data.decode()


def write_cache_file():
    """
    Write the cache file with the last visit times in encrypted format.
    :return: None
    """
    encrypted_data = encrypt_data(json.dumps(last_visit_times), encryption_key)

    with open(cache_file, "wb") as file:
        file.write(encrypted_data)

    write_logs("info", "Cache file written with last visit times")


def read_cache_file():
    """
    Read the cache file and decrypt the last visit times.
    :return: None
    """
    global last_visit_times

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as file:
            encrypted_data = file.read()

        decrypted_data = decrypt_data(encrypted_data, encryption_key)

        last_visit_times = json.loads(decrypted_data)

        write_logs("info", "Cache file read and last visit times decrypted")


if __name__ == "__main__":
    try:
        system = None

        if platform.system() == "Linux":
            system = "Linux"
        elif platform.system() == "Windows":
            system = "Windows"

        if system == 'Linux':
            if not os.geteuid() == 0:
                print("Error, Shutting Down! Only root can run this script")
                sys.exit(1)
        elif system == 'Windows':
            if not ctypes.windll.shell32.IsUserAnAdmin() != 0:
                print("Error, Shutting Down! Only root can run this script")
                sys.exit(1)

        loggingdir = None

        if system == "Linux":
            loggingdir = '/opt/browsermon'
        elif system == "Windows":
            loggingdir = 'C:\\browsermon'

        if not os.path.exists(loggingdir):
            os.makedirs(loggingdir)
            write_logs("warning",
                       f"{loggingdir} not found, creating new")

        logdir = sys.argv[1]

        if os.path.exists(logdir):
            write_logs("info",
                       f"Found logdir {logdir} for writing history files")
        else:
            os.makedirs(logdir)
            write_logs("warning",
                       f"Logdir {logdir} not found, creating new")

        last_visit_times = {}

        cache_file = os.path.join(logdir, "browsermon_cache.json")

        mode = sys.argv[2]  # Mode argument (scheduled or real-time)

        write_logs("info",
                   f"Reader started successfully in {mode} mode")

        # Path to the output file
        output_file = os.path.join(logdir, "browsermon_history.log")

        # Register the write_cache_file function to be called when the program exits
        atexit.register(write_cache_file)

        # encryption key
        passcode = '249524.405925.606329'
        encryption_key = gen_fernet_key(passcode.encode('utf-8'))

        # Read the cache file if it exists
        read_cache_file()

        scheduler = BlockingScheduler()

        if mode == "scheduled":
            schedule_window = sys.argv[3]  # Schedule window argument

            schedule_interval = parse_schedule_window(schedule_window)
            scheduler.add_job(process_edge_history, 'interval',
                              seconds=schedule_interval)

            process_edge_history()  # Run immediately when the script starts

        elif mode == "real-time":
            scheduler.add_job(process_edge_history, 'interval',
                              seconds=10)  # Run every 10 seconds

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            # Gracefully exit the scheduler
            scheduler.shutdown()

    except IndexError:
        print("Invalid number of arguments!")
        print(
            "Valid format: program [logdir] [mode](scheduled, realtime) [scheduled_window]")  # noqa
        write_logs("error", "Invalid number of arguments!")

    except Exception as e:
        print("An error occurred:")
        print(str(e))
        write_logs("error", f"Error: {str(e)}")
