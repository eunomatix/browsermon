# /****************************************************************************
#  **
#  ** Copyright (C) 2023 EUNOMATIX
#  ** This program is free software: you can redistribute it and/or modify
#  ** it under the terms of the GNU General Public License as published by
#  ** the Free Software Foundation, either version 3 of the License, or
#  ** any later version.
#  **
#  ** This program is distributed in the hope that it will be useful,
#  ** but WITHOUT ANY WARRANTY; without even the implied warranty of
#  ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  ** GNU General Public License for more details.
#  **
#  ** You should have received a copy of the GNU General Public License
#  ** along with this program. If not, see <https://www.gnu.org/licenses/>.
#  **
#  ** Contact: info@eunomatix.com
#  **
#  **************************************************************************/

import atexit
import concurrent.futures
import csv
import ctypes
import os
import platform
import signal
import sqlite3
import sys
from pathlib import Path

import orjson as json
from apscheduler.schedulers.background import BackgroundScheduler

from utils import system, logger, arch
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
    logger.info(f"Getting user profiles from user: {username}",
                extra={"log_id": 4004})
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
    logger.info(f"Sniffing users from {platform.node()}",
                extra={"log_id": 4001})
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
                                    f"for user: {username}",
                                    extra={"log_id": 4002})
                        user_profiles = get_profiles(user_profile_dir,
                                                     username)
                        profiles[username] = user_profiles
                finally:
                    winreg.CloseKey(user_key)
        except Exception as e:
            logger.error(f"Error: {str(e)}", extra={"log_id": 9001})
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
                    f"Found Microsoft Edge profile directory for user: {user}",
                    extra={"log_id": 4003})
                user_profiles = get_profiles(user_profile_dir, user)
                profiles[user] = user_profiles

    return profiles


def write_history_data(profiles, username, logmode, logdir):
    """
    Write the browsing history data for a given profile.
    :param logdir:
    :param logmode:
    :param profiles: Profiles information
    :param username: Username
    :return: None
    """
    global cache

    metadata = get_static_metadata(
        profiles[username][next(iter(profiles[username]))]["profile_path"],
        username, "edge")

    # Loop through the profiles for the given username
    for profile_name, profile_info in profiles[username].items():
        history_file = os.path.join(profile_info["profile_path"], "History")

        # Get the last modified time and last visit time for the profile
        profile_cache = cache.get(username, {}).get(profile_name, {})
        last_modified_time = profile_cache.get("last_modified_time")
        last_visit_time = profile_cache.get("last_visit_time")

        # Check if the history file has been modified since the last run
        current_modified_time = os.path.getmtime(history_file)

        if last_modified_time == current_modified_time:
            logger.info(
                f"History file for profile '{profile_name}' has not been "
                f"modified, skipping SQL query.",
                extra={"log_id": 5001})  # noqa
            continue

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
            f"user: '{metadata['os_username']}'", extra={"log_id": 5002})

        # Update the last modified time and last visit time in the cache
        profile_cache["last_modified_time"] = current_modified_time
        profile_cache["last_visit_time"] = rows[-1][
            4] if rows else last_visit_time
        cache.setdefault(username, {})[profile_name] = profile_cache

        if num_new_records == 0:
            cursor.close()
            connection.close()
            continue

        output_file = os.path.join(logdir, f"browsermon_history.{logmode}")

        file_modes = {
            'json': 'r+b',
            'csv': 'a+'
        }

        newline_arg = '' if logmode == 'csv' else None

        if logmode == "json":
            output_file = Path(output_file)
            output_file.touch(exist_ok=True)

        with open(output_file, file_modes[logmode], newline=newline_arg) as file:
            if logmode == "json":
                library = 'json_writer'

                if system == 'Linux':
                    writer = ctypes.CDLL(f'{library}_linux64.so')
                else:
                    if arch == '64bit':
                        writer = ctypes.CDLL(f'{library}_win64.dll')
                    else:
                        writer = ctypes.CDLL(f'{library}_win32.dll')
                writer.write_json_entry.argtypes = [ctypes.c_int, ctypes.c_char_p]
                writer.write_json_entry.restype = None
                file_descriptor = file.fileno()
                entry_writer = lambda x: writer.write_json_entry(file_descriptor, json.dumps(x))  # noqa
            elif logmode == "csv":
                # Prepare fieldnames dynamically from the keys of the first entry
                fieldnames = list(
                    prepare_entry(rows[0], metadata, profile_info).keys())
                csv_writer = csv.DictWriter(file, fieldnames=fieldnames)
                entry_writer = csv_writer.writerow

                # Check if the CSV file is empty and write header if needed
                if file.tell() == 0:
                    csv_writer.writeheader()

            for result in rows:
                entry = prepare_entry(result, metadata, profile_info)
                entry_writer(entry)

        cursor.close()
        connection.close()

        logger.info(f"Processed browsing history for profile '{profile_name}'",
                    extra={"log_id": 5003})


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

    # Create a ThreadPoolExecutor with a fixed thread pool size
    with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_cpu_cores) as executor:
        # Submit tasks for each username to the executor
        for username in profiles:
            try:
                logger.info(f"Processing browsing history for user: {username}",
                            extra={"log_id": 5001})
                future = executor.submit(write_history_data, profiles,
                                         username, logmode, logdir)
                future.result()  # Get the result of the task (this will
                # raise an exception if the task raised one)
            except Exception as e:
                logger.error(
                    f"Error processing history for user: {username}: {str(e)}",
                    extra={"log_id": 5001})  # Log with a specific log ID

    logger.info("Processed browsing history for all the profiles and users",
                extra={"log_id": 5004})


def cleanup_on_sigterm(signum, frame):
    sys.exit(0)


def cleanup(cache_file, encryption_key):
    # Function to be called by atexit, ensuring cache is written to the file
    write_cache_file(cache_file, encryption_key, cache)


def main(exit_feedback_queue, shared_lock, logdir, logmode, mode,
         schedule_window):
    global cache

    if system == 'Linux':
        if not os.geteuid() == 0:
            print("Error, Shutting Down! Only root can run this script")
            logger.error(
                "Shutting Down! Only root can run this script",
                extra={"log_id": 9001})  # noqa
            return
    elif system == 'Windows':
        import ctypes

        if not ctypes.windll.shell32.IsUserAnAdmin() != 0:
            print("Error, Shutting Down! Only root can run this script")
            logger.error(
                "Shutting Down! Only root can run this script",
                extra={"log_id": 9001})  # noqa
            return

    if os.path.exists(logdir):
        logger.info(f"Found logdir {logdir} for writing history files",
                    extra={"log_id": 3001})
    else:
        os.makedirs(logdir)
        logger.warning(f"Logdir {logdir} not found, creating new",
                       extra={"log_id": 3002})

    cache_file = os.path.join(logdir, "browsermon_cache")

    logger.info(f"Reader started successfully in {mode} mode",
                extra={"log_id": 1001})

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

    scheduler = BackgroundScheduler()

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
        logger.info("accquiring lock ... ", extra={"log_id": 8001})
        shared_lock.acquire()  # This will go into a blocking call if the
        # lock is already accquired, which it will be by the controller
        logger.info("accquired lock", extra={"log_id": 8002})
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        exit_feedback_queue.put("edge exited", extra={"log_id": 8003})
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {str(e)}", extra={"log_id": 9001})
        scheduler.shutdown()
        exit_feedback_queue.put("edge exited")
        sys.exit(1)

    logger.info("Exiting Edge Reader; shutting down scheduler",
                extra={"log_id": 7001})
    scheduler.shutdown()
    scheduler.remove_all_jobs()
    logger.info("Releasing lock", extra={"log_id": 7002})
    shared_lock.release()
    logger.info(
        "Sending no error in exit feedback queue; so that controller doesn't "
        "relaunch",
        extra={"log_id": 7003})
    exit_feedback_queue.put_nowait("no error")
    logger.info("Sending sys.exit(0)", extra={"log_id": 7004})
    sys.exit(0)

# if __name__ == '__main__': main(exit_feedback_queue=None,
# shared_lock=None, logdir="/opt/browsermon/history", logmode="csv",
# mode="real-time", schedule_window="1m")
