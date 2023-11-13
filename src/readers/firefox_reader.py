# ****************************************************************************
# **
# ** Copyright (C) 2023 EUNOMATIX
# ** This program is free software: you can redistribute it and/or modify
# ** it under the terms of the GNU General Public License as published by
# ** the Free Software Foundation, either version 3 of the License, or
# ** any later version.
# **
# ** This program is distributed in the hope that it will be useful,
# ** but WITHOUT ANY WARRANTY; without even the implied warranty of
# ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# ** GNU General Public License for more details.
# **
# ** You should have received a copy of the GNU General Public License
# ** along with this program. If not, see <https://www.gnu.org/licenses/>.
# **
# ** Contact: info@eunomatix.com
# **
# **************************************************************************/

import os
import glob
import sqlite3
import json
from functools import partial
import logging
import csv
import signal
import datetime
import re
import sys
import platform
from apscheduler.schedulers.background import BackgroundScheduler

from utils.metadata import has_root_privilege

entries_count = 0
scheduler = BackgroundScheduler()

system = platform.system()
default_log_loc = None

"""
Defining custom logger for Firefox Reader

"""
if default_log_loc is None:
    if system == "Linux":
        default_log_loc = "/opt/browsermon"
    elif system == "Windows":
        default_log_loc = "C:\\browsermon"
    if not os.path.exists(default_log_loc):
        os.makedirs(default_log_loc)

log_file = os.path.join(default_log_loc, "browsermon.log")
log_format = "%(asctime)s %(log_code)s:: 'Firefox Reader:' - %(levelname)s %(message)s"  # noqa

class CustomFormatter(logging.Formatter):
    def format(self, record):
        if hasattr(record, 'log_code'):
            return super().format(record)
        record.log_code = ''  # Set an empty log code if not present
        return super().format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logger level to INFO

formatter = CustomFormatter(log_format)
handler = logging.FileHandler(log_file)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_profile_folders(logdir):

    """
    Get all the profiles of the user OS
    :param Logidir :where history logs are going to be logged :
    :return: Return a Dict with OS user profle name and Profile Directory
    """
    system = platform.system()
    profile_folders = []

    if system == "Windows":
        try:
            import winreg
            reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList"
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)

            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                sid = winreg.EnumKey(reg_key, i)
                user_key = winreg.OpenKey(reg_key, sid)

                try:
                    profile_dir, _ = winreg.QueryValueEx(user_key, "ProfileImagePath")
                    username = os.path.basename(profile_dir)

                    # Filter out system-level profiles
                    if not username.lower() in ['systemprofile', 'localservice', 'networkservice']:
                        profile_folders.append({
                            'Profile Name': username,
                            'Folder Path': profile_dir
                        })

                finally:
                    winreg.CloseKey(user_key)
        except Exception as e:
            print(f"Error: {str(e)}")
    
    elif system == "Linux":
        base_path = '/home'
        excluded_folders = ['root']
        for folder_path in glob.glob(os.path.join(base_path, '*')):
          folder_name = os.path.basename(folder_path)
          if os.path.isdir(folder_path) and folder_name not in excluded_folders:
            profile_folders.append({
                'Profile Name': folder_name,
                'Folder Path': folder_path
            })
    print (profile_folders)
    return profile_folders


class FixedData:
    """
    Fixed data class 
    :param user_profile_dir:
    :return: Return a Dict with Fixed data Related to browser which is not related to history
    """
    def __init__(self, db_path=None):
        self.hostname = platform.node()
        self.os = platform.system()
        self.os_username = ""
        self.browser = "Mozilla Firefox"
        self.browser_version = self.get_firefox_version(db_path)
        self.browser_db = f"SQLite {sqlite3.sqlite_version}"

    def get_firefox_version(self, db_path=None):
        system = platform.system()
        version = ""

        if system == "Windows":
            try:
                import winreg
                reg_path = r"SOFTWARE\Mozilla\Mozilla Firefox"
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                version, _ = winreg.QueryValueEx(reg_key, "CurrentVersion")
            except Exception as e:
                # Handle the exception or log an error if needed
                version = None
        elif system == "Linux":
            prefs_file_path = db_path.replace("/places.sqlite", "/prefs.js")
            try:
                with open(prefs_file_path, 'r') as file:
                    prefs_content = file.read()

                    # Define a regular expression pattern to match the preference
                    pattern = r'user_pref\("distribution\.iniFile\.exists\.appversion",\s+"(.*?)"\);'

                    # Use re.search to find the pattern in the prefs_content
                    match = re.search(pattern, prefs_content)

                    if match:
                        # If a match is found, return the value inside the double quotes
                        version = match.group(1)
                    else:
                        # If no match is found, set version to None or a default value
                        version = None
            except Exception as e:
                # Handle the exception or log an error if needed
                version = None

        return version

def get_profile_info(database_path):
    """
    Get Information Related to Browser profile 
    :param Database path of The profile:
    :return: Return a Dict with Profile related data Email id, account id and Email
    """
    logger.info(f"database path: {database_path}")
    system = platform.system()
    if system == "Windows":
        prefs_file_path = os.path.join(os.path.dirname(database_path), "prefs.js")
    elif system == "Linux":
        prefs_file_path = os.path.join(os.path.dirname(database_path), "prefs.js")

    name_path = os.path.dirname(database_path)
    email_id= 'Not Available'
    full_name='Not Available'
    Account_id='Not Available'
    try:

        id = os.path.basename(name_path)
        pattern = r'user_pref\("services\.sync\.username", "(.*?)"\);'

        with open(prefs_file_path, 'r') as file:
            prefs_content = file.read()
            match = re.search(pattern, prefs_content)
            Account_id = id
            if match:
                email_id =  match.group(1)
                parts = email_id.split('@')
                full_name = parts[0]

                logger.info(f"Profile info found - Account ID: {Account_id}, Email ID: {email_id}, Full Name: {full_name}")


            profile_information = {
                    "email_id": email_id if email_id is not None else "Not Available",
                    "full_name": full_name if full_name is not None else "Not Available",
                    "Account_id": Account_id if Account_id is not None else "Not Available"
                
                }
            return( profile_information )
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        
        logger.error(f"No user Data found for {database_path}, exiting", extra={'log_code': 'BM9001'})
        pass
    
def filter_folders(folder_path):
    """
    Filter folder paths dict 
    :param Dict of folder paths:
    :return: Return a Dict folder paths Cleaned
    """
    excluded_items = ['Crash Reports', 'Pending Pings']

    folder_paths = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, f))
        and not any(exclude_item in f for exclude_item in excluded_items)
    ]

    return folder_paths
def get_firefox_profile_folders(logdir):
    """
    Firefox profiles Folder paths
    :param: Logdir of Firefox_profiles_data to save folder paths in json
    :return: Saves Firefox profiles Database paths in json
    """
    logdirec = logdir
    profile_data = get_profile_folders(logdirec)
    profile_objects = {}  # Initialize the profile_objects dictionary here
    Default_folder_path = []  # List to store additional folder paths

    for profile in profile_data:
        profile_name = profile['Profile Name']
        get_os_username = profile_name
        Default_folder_path = ''
        logger.info(f"Extracting user profiles from {get_os_username}", extra={'log_code': 'BM4001'})

        system = platform.system()
        if system == "Windows":
            folder_path = os.path.join('C:\\Users', get_os_username, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
        elif system == "Linux":
            folder_path = os.path.join('/home', get_os_username, '.mozilla', 'firefox')
        if not os.path.exists(folder_path):
            logger.warn(f"No Firefox profiles found for {get_os_username}, skipping", extra={'log_code': 'BM4003'})
            continue  # Skip this user

        folder_paths = filter_folders(folder_path)

        for r in range(len(folder_paths)):
            profile_folder = folder_paths[r]

            profile_info = {
                'Profile Username': get_os_username,
                'Profile Link': profile_folder,
                'Last saved value number': 0
            }
            print("Profile found for", get_os_username)
            logger.info(f"Profile found for {get_os_username}  at {profile_info['Profile Link']}", extra={'log_code': 'BM4002'})
            profile_objects[profile_folder] = profile_info  # Update the profile_objects dictionary here

    json_file_for_profiles = os.path.join(logdir, 'Firefox_profiles_data.json')
    try:
        existing_data = []
        if os.path.exists(json_file_for_profiles):
            with open(json_file_for_profiles) as existing_file:
                existing_data = json.load(existing_file)
        else:
            logger.error(f"File Not found to Write profile links, exiting", extra={'log_code': 'BM9001'})

        existing_links = {profile['Profile Link'] for profile in existing_data}
        new_profile_objects = [profile for profile in profile_objects.values() if profile['Profile Link'] not in existing_links]
        merged_data = existing_data + new_profile_objects

        with open(json_file_for_profiles, 'w') as outfile:
            json.dump(merged_data, outfile, indent=4)

    except IOError as e:
        logger.warn(f"ERROR Exception Found while writing Profiles data to JSON file: {e}", extra={'log_code': 'BM9001'})


def table_exists(cursor, table_name):
    """
    Checks if certain tables exists in the database or not
    :param: Cursor and Table name in database
    :return: If it is present or not

    """
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None


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
        logger.warn(f"Invalid schedule window format. Please use the valid format (e.g., 1m, 1h, 1d)", extra={'log_code': 'BM9001'})
        sys.exit(1)



def monitor_history_db(db_path, logdir):
    
    """
    Fetch History from database
    :param: Database Path
    :param: Logdir of history log file
    :return: Latest History Data fetched from the dabase 
    """
    if not os.path.isfile(db_path):
        logger.error(f"ERROR Database to get history logs not found for {db_path}", extra={'log_code': 'BM9001'})
        return None
     
    try:
        conn = sqlite3.connect(f"file:{db_path}?immutable=1", uri=True)
        cursor = conn.cursor()

        if not table_exists(cursor, 'moz_historyvisits'):
            return None
        
        json_file = os.path.join(logdir, 'Firefox_profiles_data.json')
        
        if os.path.exists(json_file):
    
         with open(json_file, 'r') as file:
            
            profiles = json.load(file)
            for profile in profiles:
                system = platform.system()
                if system == 'Windows':
                    if profile['Profile Link'] == os.path.normpath(db_path).replace(os.sep + 'places.sqlite', ''):
                        last_saved_value_number = profile.get('Last saved value number')
                        break
                elif system == 'Linux':
                    if profile['Profile Link'] == os.path.normpath(db_path).replace(os.path.sep + 'places.sqlite', ''):
                        last_saved_value_number = profile.get('Last saved value number')
                        break
            else:
                last_saved_value_number = None
        else:
            logger.error(f"File not found to read Profile Links", extra={'log_code': 'BM9001'})

        
        if last_saved_value_number is not None:
            query = """
                SELECT
                    hv.visit_date,  -- Specify the table name or alias for visit_date
                    mp.url,
                    mp.title,
                    mp.visit_count,
                    mr.url AS referrer_url

                FROM
                    moz_historyvisits AS hv
                    INNER JOIN moz_places AS mp ON hv.place_id = mp.id
                    LEFT JOIN moz_historyvisits AS hvc ON hv.from_visit = hvc.id
                    LEFT JOIN moz_places AS mr ON hvc.place_id = mr.id
                WHERE
                    hv.visit_date > ?;
            """
            cursor.execute(query, (last_saved_value_number,))
            history_data = cursor.fetchall()
        else:
            history_data = None

        return history_data

    except (FileNotFoundError, json.JSONDecodeError, KeyError, sqlite3.DatabaseError) as e:
        # Catch the error and log it, but do not crash the program
        logger.error(f"ERROR Exception Found while processing {db_path}: {e}", extra={'log_code': 'BM9001'})
        return None
    
    except PermissionError as pe:
        logger.error(f"Firefox-READER: WARN Permission error while reading the {db_path}: {pe}", extra={'log_code': 'BM4003'})
        return None
    finally:
        conn.close()


def write_history_data_to_json(history_data, write_file, db_path, logdirec, write_format):

    """
    Writes history Data
    :param: history_data:  History Data recived from browser database 
    :param: write_file:    Write file to write hisotry logs
    :param: db_path: Path of database  
    :param: logdirec: Log directory of Hisotory File
    :param: write_format: Write format CSV or JSon
    """

    print( "db_path used", db_path)
    process_id= 'null';
    global entries_count
    entries_count = 0 
    logger.info(f"Writing logs to browsermon_history.log in {write_format}", extra={'log_code': 'BM5001'})
    logdir = logdirec
    profile_path= db_path; 
    Profile_data = get_profile_info(db_path)  

    Os_username= db_path.split(os.path.sep)[2]

    fix_data = FixedData(db_path= db_path)

    fix_data.os_username = Os_username
    
    for entry in history_data:
        entry_data= {}
        entry_data["hostname"] = fix_data.hostname 
        entry_data["os"] = fix_data.os
        entry_data["os_username"] = fix_data.os_username
        entry_data["browser"] = fix_data.browser     
        entry_data["browser_version"] = fix_data.browser_version
        entry_data["browser_db"] = fix_data.browser_db
        if Profile_data is not None:
            # Check each field separately and provide default value if it's None
            entry_data["profile_id"] = Profile_data.get("Account_id")      
            entry_data["profile_title"] = Profile_data.get("full_name")
            entry_data["profile_username"] = Profile_data.get("email_id")
        else:
            entry_data["profile_id"] = "Not Available" 
            entry_data["profile_title"] = "Not Available"
            entry_data["profile_username"] = "Not Available"

        entry_data["Database_Path"] = profile_path
        visit_time_microseconds = entry[0] / 1000000 
        adjusted_timestamp = visit_time_microseconds - 18000
        visit_time_obj = datetime.datetime.fromtimestamp(adjusted_timestamp)
        entry_data.update({
            'session_id': process_id,
            'referrer': entry[4],
            'Url': entry[1],
            'Title': entry[2],
            'visit_date': visit_time_obj.strftime("%Y-%m-%d %H:%M:%S"),
            'visit_count': entry[3],
        })
        entries_count+=1
        try:  
          if entry_data:  # Check if data is not empty before writing to the file
           if write_format == 'json':
               with open(write_file, 'a') as file:
                  json.dump(entry_data, file, indent=4)
                  file.write(", ")   
                  file.write("\n")

           elif write_format == 'csv':
                fieldnames = ["hostname", "os", "os_username", "browser", "browser_version", "browser_db",
                               "profile_id", "profile_title", "profile_username", "Database_Path",
                                 "session_id", "referrer", "Url", "Title", "visit_date", "visit_count"
                                  ] 
                
                
                for key, value in entry_data.items():
                    if isinstance(value, str):
                       entry_data[key] = value.encode('unicode_escape').decode()
    
                with open(write_file, 'a', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if csvfile.tell() == 0:
                        writer.writeheader()
                    writer.writerow(entry_data)

          else:
            logger.info(f"No Data found for Writing:", extra={'log_code': 'BM5001'})
       
        except Exception as e:
          logger.warn(f"ERROR Exception Found while writing browsermon_history.log :" , extra={'log_code': 'BM9001'})  
                
    logger.info(f"Total {entries_count} for Profile {db_path}: are Processed ", extra={'log_code': 'BM5002'})

    entries_count = 0  # Reset the count for the next function call


def server(db_path, write_file, logdir, write_format):
    """
    Manage fecthing data and writing
    :param: write_file:    Write file to write hisotry logs
    :param: db_path: Path of database  
    :param: logdir: Log directory of Hisotory File
    :param: write_format: Write format CSV or JSon
    """
    data = monitor_history_db(db_path, logdir)
    if data:
        last_visit_time = data[-1][0]
        write_history_data_to_json(data, write_file, db_path, logdir, write_format)
        logger.info(f"Last Visit Time for {db_path}: {last_visit_time}")

        json_file_profiles = os.path.join(logdir, 'Firefox_profiles_data.json')
        if os.path.exists(json_file_profiles):
            with open(json_file_profiles, 'r') as file:
                profiles = json.load(file)

            system = platform.system()
            if system == 'Windows':
                path_format = '\\places.sqlite'
            elif system == 'Linux':
                path_format = '/places.sqlite'
            else:
                path_format = None

            if path_format is not None:
                for profile in profiles:
                    if profile['Profile Link'] == db_path.replace(path_format, ''):
                        if last_visit_time is not None:
                            profile['Last saved value number'] = last_visit_time
                        break

                with open(json_file_profiles, 'w') as file:
                    json.dump(profiles, file, indent=4)
            else:
                logger.error(f"Invalid Path:" , extra={'log_code': 'BM9001'})  

        else:
            logger.error(f"Can't find Firefox Profile Data file:" , extra={'log_code': 'BM9001'})  
    else:
        logger.info(f"No New data Found while monitoring Profile {db_path}:" , extra={'log_code': 'BM5003'})  



def process_Firefox_history(logdir, write_format):
    """
    manages os profile fetching , Browser profile Fetching and run server funtion
    :param: logdir: Log directory of Hisotory File
    :param: write_format: Write format CSV or JSon
    """
    global entries_count
    entries_count = 0 
    system = platform.system()
    profile_folders = get_profile_folders(logdir)
    Firefox_users_profiles = get_firefox_profile_folders(logdir)
    json_file_path = os.path.join(logdir, 'Firefox_profiles_data.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

            if write_format == 'json':
                write_file = os.path.join(logdir, 'browsermon_history.json')
            elif write_format == 'csv':
                write_file = os.path.join(logdir, 'browsermon_history.csv')

        for profile in json_data:
            profile_link = profile["Profile Link"]

            if system == 'Windows':
                db_path = os.path.join(profile_link, "places.sqlite")
            elif system == 'Linux':
                db_path = os.path.join(profile_link, "places.sqlite").replace("\\", "/")
            else:
                logger.error("Unsupported operating system.")
                return
            server(db_path, write_file, logdir, write_format)

    except Exception as e:
        logger.error(f"ERROR Exception Found: {e}", extra={'log_code': 'BM9001'})

def handle_signal(exit_feedback_queue, signum, frame):
    
    logger.info("Gracefully Exiting Writing funtion after reading all profiles", extra={'log_code': 'BM5003'})
    sys.exit(0)

def log_os_info():
    """
    Checks permissions and OS compatibility
    checks if script has root previlidge on linux and on windows it has adminstrative previledges
    """
    if platform.system() == "Windows":
        logger.info("Running on Windows.")
        # Add the rest of the code for Windows operations if needed.
    elif platform.system() == "Linux":
        logger.info("Running on Linux.")
        # Check if running with root privilege on Linux
        if has_root_privilege():
            logger.info("Running with root privilege.")
            # Add the rest of the code for root privileged operations on Linux if needed.
        else:
            logger.info("Not running with root privilege.")
            logger.info("Exiting the program.")
            exit()  # Exit the program if not running with root privilege on Linux.
    else:
        logger.error("Unsupported operating system.")
        logger.info("Exiting the program Due to Unsupported OS.")
        exit()  # Exit the program for unsupported operating systems.
  

def main(exit_feedback_queue, shared_lock, logdir, write_format, mode, schedule_window):
    """
    Main funtion to Run the program
    :param: exit_feedback_queue: For controller
    :param: shared_lock: Shared lock for controller
    :param: logdir: Log directory of Hisotory File
    :param: write_format: Write format CSV or JSon
    :param: mode: Either Scheduled or Real time mode
    :param: schedule_window:  If scheduled then sheduled window time
    """
    signal_handler = partial(handle_signal, exit_feedback_queue)
    signal.signal(signal.SIGTERM, signal_handler)
    log_os_info()
    if write_format == 'json':
        json_file =os.path.join(logdir, 'browsermon_history.json')

        if os.path.exists(json_file):
            logger.info(f"Found logdir {json_file} for writing history files", extra={'log_code': 'BM3001'})
        else:       
            logger.error(f"Logdir {json_file} not found, creating new", extra={'log_code': 'BM3002'})

    elif write_format == 'csv':

        csv_file =os.path.join(logdir, 'browsermon_history.csv')
        if os.path.exists(csv_file):
            logger.info(f"Found logdir {csv_file} for writing history files", extra={'log_code': 'BM3001'})
        else:       
            logger.error(f"Logdir {csv_file} not found, creating new", extra={'log_code': 'BM3002'})

    scheduler = BackgroundScheduler()
    
    logger.info(f"Reader Started successfully in {mode} mode", extra={'log_code': 'BM1001'})
    logger.info(f"Validated parameters Successfully",extra={'log_code': 'BM2001'})

    if mode == "scheduled":
        schedule_interval = parse_schedule_window(schedule_window)
        scheduler.add_job(process_Firefox_history, 'interval', args=[logdir, write_format],seconds=schedule_interval)    
    elif mode == "real-time":
        scheduler.add_job(process_Firefox_history, 'interval', args=[logdir, write_format],seconds=10)    
    else:
        logger.error(f"Issue found while processing input parameters, exiting",extra={'log_code': 'BM2002'})
    

    try:
        process_Firefox_history(logdir, write_format)
        logger.info("Firefox acquiring shared_lock ... ")
        scheduler.start()
        shared_lock.acquire()
        logger.info("Firefox accquired shared_lock")
    except (KeyboardInterrupt, SystemExit):
        logger.warn("Firefox exception caught")
        exit_feedback_queue.put("Firefox exited")
        scheduler.shutdown()
        sys.exit(1)
    except Exception as e:
        logger.warn("Came here Exception e")
        exit_feedback_queue.put("Firefox exited")
        sys.exit(1)
    
    logger.info("Firefox; shutting down scheduler")
    scheduler.shutdown()
    scheduler.remove_all_jobs()
    
    logger.info("releasing shared_lock in Firefox")
    shared_lock.release()
    exit_feedback_queue.put_nowait("no error")
    logger.info("Sending sys.exit(0)")
    sys.exit(0)
