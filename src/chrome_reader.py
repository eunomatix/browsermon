import os
import glob
import sqlite3
import json
from functools import partial
import logging
import csv
import signal
import datetime
import sys
import subprocess
import time
import platform
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

entries_count = 0
scheduler = BackgroundScheduler()

system = platform.system()
default_log_loc = None

if default_log_loc is None:
    if system == "Linux":
        default_log_loc = "/opt/browsermon"
    elif system == "Windows":
        default_log_loc = "C:\\browsermon"
    if not os.path.exists(default_log_loc):
        os.makedirs(default_log_loc)

log_file = os.path.join(default_log_loc, "browsermon.log")
log_format = "%(asctime)s %(log_code)s:: 'Google Chrome:' - %(levelname)s %(message)s"  # noqa

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


def has_root_privilege():
    """
    Check if the script has root privilege in Linux.
    :return: True if running with root privilege, False otherwise.
    """
    if platform.system() == "Linux":
        return os.geteuid() == 0
    return False

def get_chrome_version():
    system = platform.system()
    version = ""

    if system == "Windows":
        try:
            import winreg
            reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
            version, _ = winreg.QueryValueEx(reg_key, "version")
        except Exception as e:
            logger.error(f"ERROR Exception Found While Finding Chrome Version ", e ,extra= {'log_code': 'BM9001'})

    elif system == "Linux":
        try:
            cmd = "google-chrome --version"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            version = output.decode().strip().split()[-1]
        except Exception as e:
            logger.error(f"ERROR Exception Found while finding Chrome version ", e ,extra={'log_code': 'BM9001'} )

    return version

def fixed_data():
    
    Fixed_D = {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_username":"",
        "browser": "Google Chrome",
        "browser_version" :get_chrome_version(),
        "browser_db": f"SQLite {sqlite3.sqlite_version}"
    }
    return Fixed_D

def get_profile_info(database_path):
    
    logger.info(f"database path: {database_path}")
    db_path = database_path.replace("History", "Preferences")
    try:
        with open(db_path, 'r') as file:
            data = json.load(file)
            account_info = data.get("account_info")
            if account_info and isinstance(account_info, list) and len(account_info) > 0:
                account = account_info[0]
                Account_id = account.get("account_id")
                full_name = account.get("full_name")
                email_id = account.get("email")

                profile_information = {
                    "email_id": email_id if email_id is not None else "Not Available",
                    "full_name": full_name if full_name is not None else "Not Available",
                    "Account_id": Account_id if Account_id is not None else "Not Available"
                
                }
                return profile_information
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass

    return None


def get_profile_folders(logdir):
    
    system = platform.system()
    base_path = ""

    if system == "Windows":
        base_path = r'C:\Users'
        excluded_folders = ['Default', 'Public', 'All Users', 'Default User']

    elif system == "Linux":
        base_path = '/home'
        excluded_folders = ['root']

    profile_folders = []
    
    for folder_path in glob.glob(os.path.join(base_path, '*')):
        folder_name = os.path.basename(folder_path)
        if os.path.isdir(folder_path) and folder_name not in excluded_folders:
            profile_folders.append({
                'Profile Name': folder_name,
                'Folder Path': folder_path 
            })
            
    logger.info( f"OS Users Found: {profile_folders}")
    return profile_folders


def get_Chrome_profile_folders(logdir):
    logdirec=logdir
    profile_data = get_profile_folders(logdirec);
    profile_objects = {}
    Default_folder_path = []  # List to store additional folder paths

    for profile in profile_data:
        profile_name = profile['Profile Name']
        get_os_username = profile_name
        Default_folder_path= ''
        logger.info(f"Sniffing user profiles from {get_os_username}", extra={'log_code': 'BM4001'})
        system = platform.system()
        if system == "Windows":
            folder_path = os.path.join('C:\\Users', get_os_username, 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
            Default_folder_path= os.path.join('C:\\Users', get_os_username, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default')
        elif system == "Linux":
            folder_path = os.path.join('/home', get_os_username, '.config', 'google-chrome')
            Default_folder_path= os.path.join('/home', get_os_username, '.config', 'google-chrome', 'Default' )

        folder_count = sum(os.path.isdir(os.path.join(folder_path, f)) for f in os.listdir(folder_path))
        
        for r in range(1, folder_count):
            profile_folder = os.path.join(folder_path, f'Profile {r}')

            if not os.path.exists(profile_folder):
                continue

            profile_info = {
                'Profile Username': get_os_username,
                'Profile Link': profile_folder,
                'Last saved value number': 0
            }
            logger.info(f"Profile found for {get_os_username}  at {profile_info['Profile Link'] }", extra={'log_code': 'BM4002'})
            profile_objects[profile_folder] = profile_info
            if not profile_objects:
              logger.info(f"No user profiles found in {get_os_username}, exiting", extra={'log_code': 'BM4003'})
            
        new_profile_info = {
        'Profile Username': get_os_username,  # Update with the desired username
        'Profile Link': Default_folder_path,
        'Last saved value number': 0
        }
        profile_objects[profile_folder] = new_profile_info

    json_file_for_profiles = os.path.join(logdir, 'Chrome_profiles_data.json')
    try:
        existing_data = []
        if os.path.exists(json_file_for_profiles):
            with open(json_file_for_profiles) as existing_file:
                existing_data = json.load(existing_file)

        existing_links = {profile['Profile Link'] for profile in existing_data}

        new_profile_objects = [profile for profile in profile_objects.values() if profile['Profile Link'] not in existing_links]
        merged_data = existing_data + new_profile_objects

        with open(json_file_for_profiles, 'w') as outfile:
            json.dump(merged_data, outfile, indent=4)

    except IOError as e:
        logger.info(f"ERROR Exception Found while writing Profies data to JSON file: {e}", extra={'log_code': 'BM9001'})

class InvalidScheduleWindowFormat(Exception):
    """
    Custom exception for the InvalidScheduleWindowFormat
    """
    pass

def parse_schedule_window(window):

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
        logger.error(f"Invalid schedule window format. Please use the valid format (e.g., 1m, 1h, 1d)")
        sys.exit(1)


def monitor_history_db(db_path, logdir):

    if not os.path.isfile(db_path):
        return None

    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro&nolock=1', uri=True)
        cursor = conn.cursor()

        json_file = os.path.join(logdir, 'Chrome_profiles_data.json')

        with open(json_file, 'r') as file:
            profiles = json.load(file)
            for profile in profiles:
                system = platform.system()
                if system == 'Windows':
                    if profile['Profile Link'] == db_path.replace('\\History', ''):
                        last_saved_value_number = profile.get('Last saved value number')
                        break
                elif system == 'Linux':
                    if profile['Profile Link'] == db_path.replace('//History', ''):
                        last_saved_value_number = profile.get('Last saved value number')
                        break
            else:
                last_saved_value_number = None

        if last_saved_value_number is not None:
            query = """
                SELECT
                    v.visit_time,
                    urls.url,
                    urls.title,
                    urls.visit_count,
                    ca.window_id AS session_id,
                    referrer_url.url AS referrer
                FROM
                    visits AS v
                    INNER JOIN urls ON v.url = urls.id
                    LEFT JOIN context_annotations AS ca ON v.id = ca.visit_id
                    LEFT JOIN visits AS referrer_visit ON v.from_visit = referrer_visit.id
                    LEFT JOIN urls AS referrer_url ON referrer_visit.url = referrer_url.id
                WHERE
                    v.visit_time > ?
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
        logger.warning(f"CHROME-READER: WARN Permission error while reading the {db_path}: {pe}", extra={'log_code': 'BM4003'})
        return None

def write_history_data_to_json(history_data, write_file, db_path, logdirec, write_format):
    global entries_count
    entries_count = 0 
    logger.info(f"Writing logs to browsermon_history.log in {write_format}", extra={'log_code': 'BM5001'})
    logdir = logdirec
    profile_path= db_path; 
    Profile_data = get_profile_info(db_path)  
    system = platform.system()
    if system == "Windows":
        Os_username = os.path.dirname(os.path.dirname(os.path.dirname(db_path))).split(os.path.sep)[-5]
    elif system == "Linux":
        Os_username= directory_name = os.path.basename(os.path.dirname(db_path))

    fix_data = fixed_data()
    fix_data["os_username"] = Os_username
    for entry in history_data:
        entry_data= {}
        entry_data["hostname"] = fix_data.get("hostname")      
        entry_data["os"] = fix_data.get("os")
        entry_data["os_username"] = fix_data.get("os_username")
        entry_data["browser"] = fix_data.get("browser")      
        entry_data["browser_version"] = fix_data.get("browser_version")
        entry_data["browser_db"] = fix_data.get("browser_db")
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
        visit_time_microseconds = entry[0]
        visit_time_obj = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=visit_time_microseconds)
        entry_data.update({
            'session_id': entry[4],
            'referrer': entry[5],
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
            
        except Exception as e:
          logger.info(f"ERROR Exception Found while writing browsermon_history.log :" , extra={'log_code': 'BM9001'})  
                
    logger.info(f"Total {entries_count} for Profile {db_path}: are Processed ", extra={'log_code': 'BM5002'})
    entries_count = 0  # Reset the count for the next function call


def server(db_path, write_file, logdir, write_format):

    data = monitor_history_db(db_path, logdir)
    if data is not None:
        if data:
            last_visit_time = data[-1][0]
            write_history_data_to_json(data, write_file, db_path, logdir, write_format)
            logger.info(f"Last Visit Time for {db_path}: {last_visit_time}")

            json_file_profiles = os.path.join(logdir, 'Chrome_profiles_data.json')

            with open(json_file_profiles, 'r') as file:
                profiles = json.load(file)

            system = platform.system()
            if system == 'Windows':
                path_format = '\\History'
            elif system == 'Linux':
                path_format = '//History'
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

def process_chrome_history(logdir, write_format):
    global entries_count
    entries_count = 0 

    system = platform.system()
    profile_folders = get_profile_folders(logdir)
    chrome_users_profiles = get_Chrome_profile_folders(logdir)
    json_file_path = os.path.join(logdir, 'Chrome_profiles_data.json')

    try:
        with open(json_file_path, 'r') as file:
            json_data = json.load(file)

            if write_format == 'json':
                write_file = os.path.join(logdir, 'browsermon_history.json')
            elif write_format == 'csv':
                write_file = os.path.join(logdir, 'browsermon_history.csv')

        for profile in json_data:
            if system == 'Windows':
                db_path = profile["Profile Link"] + "\\History"
            elif system == 'Linux':
                db_path = profile["Profile Link"] + "//History"
            else:
                logger.error("Unsupported operating system.")
                return
            server(db_path, write_file, logdir, write_format)

    except Exception as e:
        logger.error(f"ERROR Exception Found: {e}", extra={'log_code': 'BM9001'})


def handle_signal(exit_feedback_queue, signum, frame):
    logger.info("Gracefully Exiting Writing funtion after reading all profiles", extra={'log_code': 'BM5003'})
    sys.exit(0)


def main(exit_feedback_queue, shared_lock, logdir, write_format, mode, schedule_window):

    signal_handler = partial(handle_signal, exit_feedback_queue)
    signal.signal(signal.SIGTERM, signal_handler)

    if platform.system() == "Windows":
        logger.info("Running on Windows.")
    # Add the rest of the code for Windows operations if needed.
    elif platform.system() == "Linux":
        logger.info(f"Running on Linux.")
    # Check if running with root privilege on Linux
        if has_root_privilege():
            logger.info(f"Running with root privilege.")
        # Add the rest of the code for root privileged operations on Linux if needed.
        else:
            logger.info("Not running with root privilege.")
            logger.info("Exiting the program.")
            exit()  # Exit the program if not running with root privilege on Linux.
    else:
        logger.error("Unsupported operating system.")
        logger.info("Exiting the program Due to Unsupported OS.")
        exit()  # Exit the program for unsupported operating systems.        

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

    if mode == "scheduled":
        logger.info(f"Reader Started successfully in {mode} mode", extra={'log_code': 'BM1001'})
        logger.info(f"Validated parameters Successfully",extra={'log_code': 'BM2001'})
        schedule_interval = parse_schedule_window(schedule_window)
        scheduler.add_job(process_chrome_history, 'interval', args=[logdir, write_format],seconds=schedule_interval)    
    elif mode == "real-time":
        logger.info(f"Reader Started successfully in {mode} mode", extra={'log_code': 'BM1001'})
        logger.info(f"Validated parameters Successfully",extra={'log_code': 'BM2001'})
        scheduler.add_job(process_chrome_history, 'interval', args=[logdir, write_format],seconds=5)    
    else:
        logger.error(f"Issue found while processing input parameters, exiting",extra={'log_code': 'BM2002'})
    

    try:
        process_chrome_history(logdir, write_format)
        logger.info("chrome acquiring shared_lock ... ")
        scheduler.start()
        shared_lock.acquire()
        logger.info("chrome accquired shared_lock")
    except (KeyboardInterrupt, SystemExit):
        logger.info("chrome exception caught")
        exit_feedback_queue.put("chrome exited")
        scheduler.shutdown()
        sys.exit(1)
    except Exception as e:
        print("Came here Exception e")
        exit_feedback_queue.put("chrome exited")
        sys.exit(1)
    
    logger.info("chrome; shutting down scheduler")
    scheduler.shutdown()
    scheduler.remove_all_jobs()
    
    logger.info("releasing shared_lock in chrome")
    shared_lock.release()
    exit_feedback_queue.put_nowait("no error")
    logger.info("Sending sys.exit(0)")
    sys.exit(0)
