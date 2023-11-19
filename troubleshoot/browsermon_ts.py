import subprocess
import click
import time
import uuid
import os
import json
import platform
import socket
import re
import json
import psutil
import logging
import shutil 
import zipfile 


class ShellCommandExecutor: 
    def execute(self, command: str) -> str:
        pass

class PowershellCommandExecutor(ShellCommandExecutor):
    def execute(self, command: str) -> str:
        result = subprocess.run(["powershell.exe", "-Command", command], capture_output=True, text=True)
        return result
    def check_output(self, command: str) -> str:
        output = subprocess.check_output(["powershell.exe", "-Command", command], universal_newlines=True)
        return output

class BashShellCommandExecutor(ShellCommandExecutor):
    def execute_command(self, command: str) -> str:
        """
        Execute a given shell command and return its output.

        Args:
        - command (str): The shell command to be executed.

        Returns:
        - str: The output of the executed command.
        """
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Error executing command. Error: {result.stderr}")
            return result.stdout.strip()
        except Exception as e:
            raise e

class writer: 
    def __init__(self, data, file_path):
        self.data = data
        self.file_path = file_path 
    def write(self):
        """
        Writes a dictionary to a JSON file at the specified file path.

        Parameters:
        - data (dict): The dictionary to be written to a file.
        - file_path (str): The path to the file where the data should be written.

        Returns:
        None
        """
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        if (isinstance(self.data, dict) == True): 
            with open(self.file_path, 'w', encoding='utf-8') as file:
                json.dump(self.data, file, ensure_ascii=False, indent=4)
        elif (isinstance(self.data, str) == True): 
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(self.data)

class BrowserVersionInfo:
    def __init__(self, executor):
        self.executor = executor

        if isinstance(self.executor, PowershellCommandExecutor):
            self.init_powershell()
        elif isinstance(self.executor, BashShellCommandExecutor):
            self.init_bash()

    def init_bash(self):
        commands = ['google-chrome', 'firefox', 'microsoft-edge']
        browser_versions = {}

        for cmd in commands:
            version = str(self.executor.execute([cmd, '--version']))
            browser_versions[cmd] = version.strip()

        self.writer = writer(browser_versions, "browser_info.json").write()

    def init_powershell(self):
        self.browser_info_win() 
        pass
    
    def get_version_via_com(self, filename):
        from win32com.client import Dispatch
        parser = Dispatch("Scripting.FileSystemObject")
        try:
            version = parser.GetFileVersion(filename)
        except Exception:
            return None
        return version
    
    def browser_info_win(self):
        browsers = {
            "Chrome": [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ],
            "Firefox": [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
            ],
            "Edge": [
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
        }

        browser_versions = {}

        for browser, paths in browsers.items():
            version = list(filter(None, [self.get_version_via_com(p) for p in paths]))
            if version:
                browser_versions[browser] = version[0]
            else:
                browser_versions[browser] = "Not Found"
        # Save to JSON file
        self.writer = writer(browser_versions, "browser_info.json").write()
        print("Browser information saved to browser_info.json")

class systemInfo: 
    def __init__(self, executor):
        self.executor = executor

        if isinstance(self.executor, PowershellCommandExecutor):
            self.getsysinfo()
        elif isinstance(self.executor, BashShellCommandExecutor):
            self.getsysinfo()
    
    def getsysinfo(self):
        try:
            info = {}
            info['platform'] = platform.system()
            info['platform-release'] = platform.release()
            info['platform-version'] = platform.version()
            info['architecture'] = platform.machine()
            info['hostname'] = socket.gethostname()
            info['ip-address'] = socket.gethostbyname(socket.gethostname())
            info['mac-address'] = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
            info['processor'] = platform.processor()
            info['ram'] = str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + " GB"
            sysinfo = json.dumps(info)
        except Exception as e:
            logging.exception(e)
        
        self.writer = writer(sysinfo, "system_info.json").write()
    

class ServiceInfo: 
    def __init__(self, executor, service_name):
        self.executor = executor   
        self.service_name = service_name
        if isinstance(self.executor, PowershellCommandExecutor):
            self.get_service_details_win(self.service_name)
        if isinstance(self.executor, BashShellCommandExecutor):
            self.get_service_details_linux(self.service_name)

    def get_service_details_win(self, service_name):
        # Define the PowerShell command

        command = f"Get-WmiObject -Class Win32_Service | Where-Object {{$_.Name -eq '{service_name}'}} | Format-List * | Out-String -Width 4096"

        # Execute the command and get the output
        output = self.executor.check_output(command) 
        details = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                details[key.strip()] = value.strip()

        writer(details, "service_info.json").write()
    
    def get_service_details_linux(self, service_name): 
        output = self.executor.execute_command(f"systemctl status {service_name} --no-pager")

        lines = [line.strip() for line in output.split("\n") if len(line.strip()) > 1]

        service_data = {}

        service_data["Service Name and Description"] = lines[0].split("●")[1].strip()

        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                service_data[key.strip()] = value.strip()

        writer(service_data, "service_info.json").write()

        output = self.executor.execute_command(f"systemctl show {service_name} --no-pager")
        data_list = output.split('\n')
        data_dict = {}
        for item in data_list: 
            if '=' in item: 
                key, value = item.split("=", 1)
                data_dict[key] = value
            else: 
                print("skipped line")
        
        writer(data_dict, "service_info_show.json").write()

        output = self.executor.execute_command(f"journalctl -u {service_name}.service --no-pager")
        output = output.split('\n')
        output = str(output)
        writer(output, "service_info_journalctl.txt").write()

class procmon: 
    def __init__(self, executor):
        self.executor = executor
        if isinstance(self.executor, PowershellCommandExecutor):
            self.restart_service()
            self.run_procmon_command()
        elif isinstance(self.executor, BashShellCommandExecutor):
            print("Procmon is not supported on bashShell")

    def restart_service(self):
        command = "Restart-Service -Name browsermon"        
        print("Restarting the service")
        #self.executor.execute(command)

    def run_procmon_command(self):
        command = ".\Procmon.exe /Minimized /Quiet /LoadConfig browsermon_procmonConfig.pmc /Backingfile browsermon_log.pml"
        print("Opening procmon")
        self.executor.execute(command)

def zipdir(source_files, dest_folder): 
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    for file in source_files: 
        shutil.copy(file, dest_folder)

    zip_file_name = "browsermon_archive.zip"        

    with zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dest_folder):
            for file in files:
                file_path = os.path.join(root, file)
                # Write the file's archive name relative to the destination folder
                archive_name = os.path.relpath(file_path, dest_folder)
                zipf.write(file_path, archive_name)

def get_browsermon_events():
    cmd = 'wevtutil qe Application /c:5 /rd:true /f:text /q:"*[System[Provider[@Name=\'browsermon\']]]" > browsermon_events.txt'
    result = subprocess.run(["powershell.exe", "-Command", cmd], capture_output=True, text=True)


logs_list_win = [
    "browser_info.json",
    "system_info.json",
    "service_info.json",
    "browsermon_events.txt",
    "browsermon_log.pml", 
    "C:\\browsermon\\browsermon.log", 
] 

logs_list_linux = [
    "browser_info.json",
    "system_info.json",
    "service_info.json", 
    "service_info_show.json",
    "service_info_journalctl.txt"
]

def get_metadata(file_path, write_to):
    file_info = os.stat(file_path)
    write_this = {
        "file_name": os.path.basename(file_path),
        "file_size": file_info.st_size,
        "file_ctime": file_info.st_ctime,
        "file_mtime": file_info.st_mtime,
        "file_atime": file_info.st_atime,
    }
    writer(file_info, write_to).write()



# Click group for organizing commands
@click.group()
def cli():
    pass

@cli.command()
@click.argument('service_name', default="browsermon")
@click.option('--logs-dir', default="C:\\browsermon\\" if platform.system() == "Windows" else "/opt/browsermon/", help='Directory to store logs', type=click.Path())
def troubleshoot(service_name, logs_dir):
    print(".....Starting troubleshooting.....")
    if platform.system() == "Windows":
        print("Running on Windows")
        executor = PowershellCommandExecutor()
    elif platform.system() == "Linux":
        print("Running on Linux")
        executor = BashShellCommandExecutor()
    else:
        print("Unsupported OS")
        ctx.exit(1)

    # Execute common steps for both platforms
    print("Getting system information")
    time.sleep(1)  # Simulate time delay for fetching information
    systemInfo(executor)
    print("System information fetched")

    print("Fetching browser information")
    time.sleep(1)
    BrowserVersionInfo(executor)
    print("Browser information fetched")

    print("Fetching service information")
    time.sleep(1)
    ServiceInfo(executor, service_name)
    print("Service information fetched")

    if platform.system() == "Windows":
        print("Getting browsermon events")
        time.sleep(1)
        get_browsermon_events()
        print("Browsermon events fetched")

        print("Running procmon, this will open procmon in a separate window. Let it run for 2 minutes, then close procmon to stop this process.")
        procmon(executor)
        print("Procmon exited")

        print("Generating zip file")
        zipdir(logs_list_win, logs_dir)
        print("Zip file generated")
    else: 
        print("Generating zip file")
        zipdir(logs_list_linux, logs_dir)
        print("Zip file generated")

    print("Troubleshooting complete; exiting")

if __name__ == "__main__":
    cli()
     