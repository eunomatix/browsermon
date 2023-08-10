import atexit
import concurrent.futures
import csv
import os
import platform
import signal
import sqlite3
import sys

import orjson as json
from apscheduler.schedulers.blocking import BlockingScheduler

from utils import system, logger
from utils.caching import write_cache_file, read_cache_file
from utils.common import parse_schedule_window, prepare_entry
from utils.encryption import gen_fernet_key
from utils.metadata import get_static_metadata

# Global variable
cache = {}


def get_profiles(user_profile_dir, username):
    """
    Get all the profiles of the user
    :param user_profile_dir:
    :param username:
    :return:
    """
    logger.info(f"Sniffing user profiles from user: {username}")
    local_state_file = os.path.join(user_profile_dir, "Local State")
    with open(local_state_file, "r") as file:
        data = json.loads(file.read())

    profile_info = data.get("profile")
    profiles = {}
    if profile_info and "info_cache" in profile_info:
        profiles = {profile_name: {"profile_id": user_data.get("gaia_id"),
                                   "profile_title": user_data.get("name"),
                                   "profile_username": user_data.get(
                                       "user_name"),
                                   "profile_path": os.path.join(
                                       user_profile_dir, profile_name),
                                   "username": username, } for
                    profile_name, user_data in
                    profile_info["info_cache"].items()}

    return profiles


def get_all_profiles():
    """
    Get all the profiles for all the users on the operating system.
    :return: Dictionary of profiles
    """
    logger.info(f"Sniffing users from {platform.node()}")
    profiles = {}

    if system == "Windows":
        import winreg

        reg_key = None

        try:
            reg_path = r"SOFTWARE\Microsoft\Windows " \
                       r"NT\CurrentVersion\ProfileList"
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                sid = winreg.EnumKey(reg_key, i)
                user_key = winreg.OpenKey(reg_key, sid)
                try:
                    profile_dir, _ = winreg.QueryValueEx(user_key,
                                                         "ProfileImagePath")
                    username = os.path.basename(profile_dir)
                    user_profile_dir = os.path.join(profile_dir, "AppData",
                                                    "Local", "Microsoft",
                                                    "Edge", "User Data")
                    if os.path.exists(user_profile_dir):
                        logger.info(f"Found Microsoft Edge profile directory "
                                    f"for user: {username}")
                        user_profiles = get_profiles(user_profile_dir,
                                                     username)
                        profiles.update(user_profiles)
                finally:
                    winreg.CloseKey(user_key)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
        finally:
            if reg_key is not None:
                winreg.CloseKey(reg_key)
    else:  # Assume Linux
        for user in os.listdir('/home'):
            user_profile_dir = os.path.join('/home', user, '.config',
                                            'microsoft-edge')

            # Check if the user has a Microsoft Edge profile directory
            if os.path.exists(user_profile_dir):
                logger.info(
                    f"Found Microsoft Edge profile directory for user: {user}")
                user_profiles = get_profiles(user_profile_dir, user)
                profiles.update(user_profiles)

    return profiles


def write_history_data(profile, logmode, logdir):
    """
    Write the browsing history data for a given profile.
    :param logdir:
    :param logmode:
    :param profile: Profile information
    :return: None
    """
    global cache

    metadata = get_static_metadata(profile["profile_path"],
                                   profile["username"], "edge")

    history_file = os.path.join(profile["profile_path"], "History")

    del profile["username"]

    profile_name = os.path.basename(profile['profile_path'])

    # Get the last modified time and last visit time for the profile
    profile_info = cache.get(profile_name, {})
    last_modified_time = profile_info.get("last_modified_time")
    last_visit_time = profile_info.get("last_visit_time")

    # Check if the history file has been modified since the last run
    current_modified_time = os.path.getmtime(history_file)

    if last_modified_time == current_modified_time:
        logger.info(
            f"History file for profile '{profile_name}' has not been modified, skipping SQL query.")  # noqa
        return

    connection = sqlite3.connect(f"file:{history_file}?immutable=1", uri=True)
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

    if last_visit_time:
        # Filter for new records based on last processed visit time
        query += " WHERE v.visit_time > ?"
        cursor.execute(query, (last_visit_time,))
    else:
        cursor.execute(query)
    rows = cursor.fetchall()

    num_new_records = len(rows)

    logger.info(
        f"Found {num_new_records} new records for profile '{profile_name}' "
        f"user: '{metadata['os_username']}'")

    # Update the last modified time and last visit time
    profile_info["last_modified_time"] = current_modified_time
    profile_info["last_visit_time"] = rows[-1][4] if rows else last_visit_time
    cache[profile_name] = profile_info

    if num_new_records == 0:
        cursor.close()
        connection.close()
        return

    output_file = os.path.join(logdir, f"browsermon_history.{logmode}")

    with open(output_file, "a+", newline='') as file:
        if logmode == "json":
            writer = lambda x: file.write(  # noqa
                json.dumps(x, option=json.OPT_INDENT_2).decode() + ",\n")
        elif logmode == "csv":
            # Prepare fieldnames dynamically from the keys of the first entry
            fieldnames = list(prepare_entry(rows[0], metadata, profile).keys())
            csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer = csv_writer.writerow

            # Check if the CSV file is empty and write header if needed
            if file.tell() == 0:
                csv_writer.writeheader()

        for result in rows:
            entry = prepare_entry(result, metadata, profile)
            writer(entry)

    cursor.close()
    connection.close()

    logger.info(f"Processed browsing history for profile '{profile_name}'")


def process_edge_history(logmode, logdir):
    """
    Process the Edge browsing history and write it to the output file using a
    dynamic thread pool.
    :param logmode:
    :param logdir:
    :return:
    """
    profiles = get_all_profiles()

    num_cpu_cores = os.cpu_count()
    num_profiles = len(profiles)

    # Choose the minimum value between the number of CPU cores and the
    # number of profiles as the thread pool size #noqa
    max_workers = min(num_cpu_cores, num_profiles)

    # Create a ThreadPoolExecutor with the dynamic thread pool size
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers) as executor:
        # Submit tasks for each profile to the executor
        future_to_profile = {
            executor.submit(write_history_data, profile, logmode,
                            logdir): profile for profile in profiles.values()}

        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(future_to_profile):
            profile = future_to_profile[future]
            try:
                future.result()  # Get the result of the task
                # (this will raise an exception if the task raised one)
            except Exception as e:
                logger.error(
                    f"Error processing history for profile '{profile['profile_path']}': {str(e)}")  # noqa

    logger.info("Processed browsing history for all the profiles and users")


def cleanup_on_sigterm(signum, frame):
    sys.exit(0)


def cleanup(cache_file, encryption_key):
    # Function to be called by atexit, ensuring cache is written to the file
    write_cache_file(cache_file, encryption_key, cache)


def main(exit_feedback_queue, logdir, logmode, mode, schedule_window):
    sys.stdout = open(str(os.getpid()) + ".out", "a")
    sys.stderr = open(str(os.getpid()) + "_error.out", "a")
    global cache
    if system == 'Linux':
        if not os.geteuid() == 0:
            print("Error, Shutting Down! Only root can run this script")
            logger.error(
                "Shutting Down! Only root can run this script")  # noqa
            return
    elif system == 'Windows':
        import ctypes

        if not ctypes.windll.shell32.IsUserAnAdmin() != 0:
            print("Error, Shutting Down! Only root can run this script")
            logger.error(
                "Shutting Down! Only root can run this script")  # noqa
            return

    if os.path.exists(logdir):
        logger.info(f"Found logdir {logdir} for writing history files")
    else:
        os.makedirs(logdir)
        logger.warning(f"Logdir {logdir} not found, creating new")

    cache_file = os.path.join(logdir, "browsermon_cache")

    logger.info(f"Reader started successfully in {mode} mode")

    # encryption key
    password = 'EunoMatix_BrowserMon'
    encryption_key = gen_fernet_key(password)

    # Register the write_cache_file function to be called when the
    # program exits
    atexit.register(cleanup, cache_file, encryption_key)

    # Set up the signal handler with the cleanup function
    signal.signal(signal.SIGTERM, cleanup_on_sigterm)

    # Read the cache file if it exists
    cache = read_cache_file(cache_file, encryption_key)

    scheduler = BlockingScheduler()

    if mode == "scheduled":
        schedule_interval = parse_schedule_window(schedule_window)
        scheduler.add_job(process_edge_history, 'interval',
                          seconds=schedule_interval,
                          args=(logmode, logdir))  # noqa

    elif mode == "real-time":
        scheduler.add_job(process_edge_history, 'interval', seconds=10,
                          args=(logmode, logdir))  # Run every 10 seconds

    try:
        # Run the main function directly when the program starts
        process_edge_history(logmode, logdir)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        exit_feedback_queue.put("edge exited")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        scheduler.shutdown()
        exit_feedback_queue.put("edge exited")
        sys.exit(1)
