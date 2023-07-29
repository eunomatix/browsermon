import multiprocessing
import os
import glob
import sqlite3
import json
import logging
import csv
import datetime
import sys
import subprocess
import time
import platform
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
entries_count = 0
scheduler = BlockingScheduler()

def write_logs(level, message, logdir):
    """
    
    Write logs to the log file
    :param level: Log level (info, error, warning)
    :param message: Log message
    :param logdir: Path to the log directory
    :return: None
    """
    if logdir is None:
        print("Error: logdir is not set.")
        return
    
    log_file = os.path.join(logdir, "browsermon.log")
    log_format = "%(asctime)s BM%(process)d:: 'Chrome:' - %(levelname)s %(message)s"
    logging.basicConfig(filename=log_file, level=logging.INFO, format=log_format)

    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    elif level == "warning" or level == "warn":
        logging.warning(message)

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
            print("Error:", e)

    elif system == "Linux":
        try:
            cmd = "google-chrome --version"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            version = output.decode().strip().split()[-1]
        except Exception as e:
            print("Error:", e)

    return version

def fixed_data():
    
    Fixed_D = {
        "hostname": platform.node(),
        "os": platform.system(),
        "browser": "Google Chrome",
        "chrome_version" :get_chrome_version(),
        "browser_db": f"SQLite {sqlite3.sqlite_version}"
    }
    return Fixed_D

def get_profile_info(database_path):
    print(database_path)
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
            
    write_logs("Info",f"OS Users Found: {profile_folders}", logdir)
    return profile_folders


def get_Chrome_profile_folders(logdir):
    logdirec=logdir
    profile_data = get_profile_folders(logdirec);
    profile_objects = {}
    for profile in profile_data:
        profile_name = profile['Profile Name']
        get_os_username = profile_name
        write_logs("info",f"Sniffing user profiles from user: {get_os_username}", logdir)

        system = platform.system()
        
        if system == "Windows":
            folder_path = os.path.join('C:\\Users', get_os_username, 'AppData', 'Local', 'Google', 'Chrome', 'User Data')

        elif system == "Linux":
            folder_path = os.path.join('/home', get_os_username, '.config', 'google-chrome')
            

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
            write_logs("info",f"Profile Found For Windows User {get_os_username} at path :{profile_info['Profile Link'] }",logdir)
            profile_objects[profile_folder] = profile_info
            if not profile_objects:
              write_logs("info", f"No Chrome user found in: {get_os_username}", logdir)

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
        print(f"Error occurred while writing to JSON file: {e}")
        
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
        print("Invalid schedule window format. Please use the valid format (e.g., 1m, 1h, 1d)")
        sys.exit(1)


def monitor_history_db(client_pipe, db_path, logdir):
    if not os.path.isfile(db_path):
        return

    try:
        conn = sqlite3.connect(f'file:{db_path}?mode=ro&nolock=1', uri=True)
        cursor = conn.cursor()

        # Load the last saved value number for the profile from the Chroeme_profiles_data.json file
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
            # Modify the SQL query to fetch additional columns: visit_count, window_id (session_id), referrer
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

        client_pipe.send(history_data) 
    except (FileNotFoundError, json.JSONDecodeError, KeyError, sqlite3.DatabaseError) as e:
        # Catch the error and log it, but do not crash the program
        write_logs("error", f"Error while processing {db_path}: {e}", logdir)
        client_pipe.send(None)  # Send None to indicate failure



def write_history_data_to_json(history_data, write_file, db_path, logdirec, write_format):
    global entries_count
    entries_count = 0 
    write_logs("Info",f"writing history database:", logdirec)
    
    logdir = logdirec
    profile_path= db_path; 
    Profile_data = get_profile_info(db_path)  
    system = platform.system()

       
    if system == "Windows":
        Os_username = os.path.dirname(os.path.dirname(os.path.dirname(db_path))).split(os.path.sep)[-5]
    elif system == "Linux":
        Os_username= directory_name = os.path.basename(os.path.dirname(db_path))

    entry_data=[]
    data = []
    fix_data = fixed_data()
    for entry in history_data:
        visit_time_microseconds = entry[0]
        visit_time_obj = datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=visit_time_microseconds)
        entry_data = {
            'Visit time (UTC)': visit_time_obj.strftime("%Y-%m-%d %H:%M:%S"),
            'Url': entry[1],
            'Title': entry[2],
            'visit_count': entry[3],
            'window_id': entry[4],
            'referrer_url': entry[5]
        }
        if Profile_data is not None:
            # Check each field separately and provide default value if it's None
            entry_data["email_id"] = Profile_data.get("email_id")
            entry_data["full_name"] = Profile_data.get("full_name")
            entry_data["Account_id"] = Profile_data.get("Account_id")      
        else:
            entry_data["email_id"] = "Not Available"
            entry_data["full_name"] = "Not Available"
            entry_data["Account_id"] = "Not Available"    
        
        entry_data.update(fix_data)
        entry_data["Os_user"] = Os_username
        entry_data["Database_Path"] = profile_path
         
        entries_count += 1
        data.append(entry_data)
        
    try:
        
        if data:  # Check if data is not empty before writing to the file

          if write_format == 'json':
              with open(write_file, 'a') as file:
                  json.dump(data, file, indent=4)
                  write_logs("Info", f"Total Number of Entries found for {db_path}: are {entries_count}", logdir)
          elif write_format == 'csv':
                fieldnames = ['Visit time (UTC)', 'Url', 'Title', 'visit_count', 'window_id', 'referrer_url',
                              'email_id', 'full_name', 'Account_id', 'hostname', 'os', 'browser', 'chrome_version',
                              'browser_db', 'Os_user', 'Database_Path']

                with open(write_file, 'a', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    if csvfile.tell() == 0:
                        writer.writeheader()

                    writer.writerows(data)       
                
    except Exception as e:
        write_logs("Info", f"writing history database:", logdir)  # Pass logdir as an argument

    entries_count = 0  # Reset the count for the next function call


def server(db_path, write_file, logdir, write_format):
    global entries_count
    entries_count = 0
    server_pipe, client_pipe = multiprocessing.Pipe()
    server_process = multiprocessing.Process(target=monitor_history_db, args=(client_pipe, db_path, logdir))
    server_process.start()

    last_visit_time = None
    json_file_profiles = os.path.join(logdir, 'Chrome_profiles_data.json')

    data = server_pipe.recv()
    if data is not None:
        if data:
            last_visit_time = data[-1][0]
        write_history_data_to_json(data, write_file, db_path, logdir, write_format)
        print(f"Last Visit Time for {db_path}: {last_visit_time}")

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

    server_process.terminate()


def process_chrome_history(logdir, write_format):
    global entries_count
    entries_count = 0 
    profile_folders = get_profile_folders(logdir)
    chrome_users_profiles = get_Chrome_profile_folders(logdir)
    json_file_path = os.path.join(logdir, 'Chrome_profiles_data.json')

    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    processes = []
    last_visit_times = {}

    for profile in json_data:
        system = platform.system()
        if system == 'Windows':
            db_path = profile["Profile Link"] + "\\History"
        elif system == 'Linux':
            db_path = profile["Profile Link"] + "//History"
        else:
            print("Unsupported operating system.")
            continue
        
        if write_format == 'json':
           write_file = os.path.join(logdir, 'browsermon_history.json')
        elif write_format == 'csv':
           write_file = os.path.join(logdir, 'browsermon_history.csv')

        process = multiprocessing.Process(target=server, args=(db_path, write_file, logdir, write_format))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
        
def real_time_execution(logdir , write_format):
    # Add the job to the scheduler
    scheduler.add_job(process_chrome_history, 'interval', args=[logdir, write_format], seconds=5)

    while True:
        try:
            # Start the scheduler (only once)
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            # Gracefully exit the scheduler
            scheduler.shutdown()
            break
        except Exception as e:
            # Handle any unexpected exceptions, log them, and retry
            write_logs("error", f"An unexpected error occurred: {e}", logdir)
            time.sleep(5)  # Wait for a while before retrying

        # If the scheduler has stopped, wait for a while before retrying
        time.sleep(5)


if __name__ == '__main__':

    try:
        logdir = sys.argv[1]
        write_format= sys.argv[2]
            # Check the operating system
        if platform.system() == "Windows":
           write_logs("info", "Running on Windows.", logdir)
        # Add the rest of the code for Windows operations if needed.
        elif platform.system() == "Linux":
           write_logs("info", "Running on Linux.", logdir)
        # Check if running with root privilege on Linux
        #    if has_root_privilege():
        #        write_logs("Info", "Running with root privilege.", logdir)
        #     # Add the rest of the code for root privileged operations on Linux if needed.
        #    else:
        #       write_logs("Info", "Not running with root privilege.", logdir)
        #       write_logs("Info", "Exiting the program.", logdir)
        #       exit()  # Exit the program if not running with root privilege on Linux.
        else:
          write_logs("error", "Unsupported operating system.", logdir)
          write_logs("info", "Exiting the program.", logdir)
          exit()  # Exit the program for unsupported operating systems.        

        if write_format == 'json':
            json_file =os.path.join(logdir, 'browsermon_history.json')

            if os.path.exists(json_file):
                write_logs("info", f"Found History File {json_file} for writing history files", logdir)
            else:       
               write_logs("Info", f"Does not find files TO write Creating A new FIle", logdir)

        elif write_format == 'csv':

            csv_file =os.path.join(logdir, 'browsermon_history.csv')
            if os.path.exists(csv_file):
                write_logs("info", f"Found History File {csv_file} for writing history files", logdir)
            else:       
               write_logs("Info", f"Does not find files TO write Creating A new FIle", logdir)


        mode = sys.argv[3] 
        

        if mode == "scheduled":
            write_logs("info", f"Validated parameters Successfully", logdir)
            write_logs("info", f"Reader started successfully in {mode} mode", logdir)
            schedule_window = sys.argv[4]  # Schedule window argument
            schedule_interval = parse_schedule_window(schedule_window)
            scheduler = BlockingScheduler(max_instances= None)

            scheduler.add_job(process_chrome_history, 'interval', args=[logdir, write_format], seconds=schedule_interval)

            try:
                scheduler.start()
            except (KeyboardInterrupt, SystemExit):
                # Gracefully exit the scheduler
                write_logs("info", f"Exiting the Controller after Keyboard inturrupt", logdir)

                scheduler.shutdown()
            
        elif mode == "real-time":
            write_logs("info", f"Validated parameters Successfully", logdir)
            write_logs("info", f"Reader started successfully in {mode} mode", logdir)

            # Call the real_time_execution function to start the scheduler
            real_time_execution(logdir, write_format)

    except IndexError:
        print("Invalid number of arguments!")
        print("Valid format: program [logdir] [mode](scheduled, realtime) [scheduled_window]")
        write_logs("error", f"Error: Error with input parameters", logdir)
        exit()  # Exiting the program