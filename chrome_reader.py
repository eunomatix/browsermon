import json
import sys
import time

def write_to_json_file(file_path, data):
    with open(file_path, 'a') as file:
        json.dump(data, file)
        file.write('\n')

try: 
    file_path = 'file.json'
    while True:
        data = {'timestamp': time.time(), 'value': 42}
        write_to_json_file(file_path, data)
        time.sleep(1)
        
except KeyboardInterrupt:
    #doing this so that controller doesn't relaunch the reader
    print("Sending exit code 0")
    sys.exit(0) 
    