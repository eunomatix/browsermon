import multiprocessing
import os
import glob
import sqlite3
import json
import sys
import winreg
import time
import platform
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

def get_chrome_version():
    try:
        reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_32KEY)
        version, _ = winreg.QueryValueEx(reg_key, "version")
        return version
    
    except Exception as e:
        print("Error:", e)
        return None

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

    

def get_profile_folders():
    base_path = r'C:\Users'
    excluded_folders = ['Default', 'Public','All Users', 'Default User']

    profile_folders = []

    for folder_path in glob.glob(os.path.join(base_path, '*')):
        folder_name = os.path.basename(folder_path)
        if os.path.isdir(folder_path) and folder_name not in excluded_folders:
            profile_folders.append({
                'Profile Name': folder_name,
                'Folder Path': folder_path 
            })

    return profile_folders


def write_profile_folders_to_json(profile_folders):
    file_path = 'windows_users.json'
    with open(file_path, 'w') as file:
        json.dump(profile_folders, file, indent=4)



def get_Chrome_profile_folders():
 with open('windows_users.json') as file:
    profile_data = json.load(file)

 profile_objects = {}

 for profile in profile_data:
    profile_name = profile['Profile Name']
    get_window_username = profile_name
    folder_path = os.path.join('C:\\Users', get_window_username, 'AppData', 'Local', 'Google', 'Chrome', 'User Data')
    folder_count = sum(os.path.isdir(os.path.join(folder_path, f)) for f in os.listdir(folder_path))
    
    for r in range(1, folder_count):
        profile_folder = os.path.join(folder_path, f'Profile {r}')
        if not os.path.exists(profile_folder):
            continue

        profile_info = {
            'Profile Username': get_window_username,
            'Profile Link': profile_folder,
            'Last saved value number': 0
        }

        profile_objects[profile_folder] = profile_info

 json_file = 'profile_info_with_check.json'

 try:
    existing_data = []
    if os.path.exists(json_file):
        with open(json_file) as existing_file:
            existing_data = json.load(existing_file)
    
    existing_links = {profile['Profile Link'] for profile in existing_data}
    
    new_profile_objects = [profile for profile in profile_objects.values() if profile['Profile Link'] not in existing_links]
    merged_data = existing_data + new_profile_objects
    
    with open(json_file, 'w') as outfile:
        json.dump(merged_data, outfile, indent=4)
        
 except IOError as e:
    print(f"Error occurred while writing to JSON file: {e}")

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


def monitor_history_db(client_pipe, db_path):
    if not os.path.isfile(db_path):
        client_pipe.send('Invalid file path')
        return
    conn = sqlite3.connect(f'file:{db_path}?mode=ro&nolock=1', uri=True)
    cursor = conn.cursor()

    # Load the last saved value number for the profile from the profile_info_with_check.json file

    with open('profile_info_with_check.json', 'r') as file:
        profiles = json.load(file)
        for profile in profiles:
            if profile['Profile Link'] == db_path.replace('\\History', ''):
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


def write_history_data_to_json(history_data, json_file, db_path):
    profile_path= db_path; 
    Profile_data = get_profile_info(db_path) 
    Windows_username= Windows_username = os.path.dirname(os.path.dirname(os.path.dirname(db_path))).split(os.path.sep)[-5]

    entry_data=[]
    data = []
    fix_data = fixed_data()

    for entry in history_data:
        entry_data = {
            'Visit time': entry[0],
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
        entry_data["Windows_user"] = Windows_username
        entry_data["Database_Path"] = profile_path
        

        data.append(entry_data)

    with open(json_file, 'a') as file:
        
        json.dump(data, file, indent=4)



def server(db_path, json_file):
    server_pipe, client_pipe = multiprocessing.Pipe()
    server_process = multiprocessing.Process(target=monitor_history_db, args=(client_pipe, db_path))
    server_process.start()

    last_visit_time = None

    while True:
        data = server_pipe.recv()
        if data == 'Invalid file path':
            print(f'Invalid file path for {db_path}. Please check the path to the Chrome history database file.')
        else:

            if data:
                last_visit_time = data[-1][0]

            write_history_data_to_json(data, json_file, db_path)
        # Print the last visit time for the current profile
        print(f"Last Visit Time for {db_path}: {last_visit_time}")
        with open('profile_info_with_check.json', 'r') as file:
            profiles = json.load(file)
        # Update the matching profile
        for profile in profiles:
            if profile['Profile Link'] == db_path.replace('\\History', ''):    
                if last_visit_time is not None:      
                 profile['Last saved value number'] = last_visit_time
                break  # Exit the loop after updating the first matching profile

        # Save the updated list back to the JSON file
        with open('profile_info_with_check.json', 'w') as file:
            json.dump(profiles, file, indent=4)
    server_process.join()


def process_chrome_history():

    profile_folders = get_profile_folders()
    write_profile_folders_to_json(profile_folders)
    chrome_users_profiles= get_Chrome_profile_folders()

    json_file_path = 'profile_info_with_check.json'

    with open(json_file_path, 'r') as file:
        json_data = json.load(file)

    processes = []
    last_visit_times = {}

    for profile in json_data:
        db_path = profile["Profile Link"] + "\\History"
        json_file = 'history_data_while_visits.json'
        process = multiprocessing.Process(target=server, args=(db_path, json_file))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()   

def real_time_execution():

    scheduler = BackgroundScheduler(max_instances=None)  # Set max_instances to None for unlimited instances
    scheduler.add_job(process_chrome_history, 'interval', seconds=10)
    scheduler.start()

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

if __name__ == '__main__':
    try:
        mode = sys.argv[2]  # Mode argument (scheduled or real-time)

        if mode == "scheduled":
            schedule_window = sys.argv[3]  # Schedule window argument
            schedule_interval = parse_schedule_window(schedule_window)

            scheduler = BlockingScheduler(max_instances= None)
            scheduler.add_job(process_chrome_history, 'interval', seconds=schedule_interval)

            try:
                scheduler.start()
            except (KeyboardInterrupt, SystemExit):
                # Gracefully exit the scheduler
                scheduler.shutdown()

        elif mode == "real-time":
            real_time_execution()

    except IndexError:
        print("Invalid number of arguments!")
        print("Valid format: program [logdir] [mode](scheduled, realtime) [scheduled_window]")