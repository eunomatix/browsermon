import re
import os
import time
import logging 
import queue
import platform
import subprocess
import multiprocessing
import configparser
from logging.handlers import RotatingFileHandler

import launcher
import handlers

class BrowsermonController:
    def __init__(self):
        self.SYSTEM = platform.system()
        self.logger = self.init_logger()
        self.launcherObj = None

    def init_logger(self):
       
        if self.SYSTEM == "Windows":
            log_file = "C:\\browsermon\\browsermon.log"
        elif self.SYSTEM == "Linux":
            log_file = "/opt/browsermon/browsermon.log"

        handler = RotatingFileHandler(
            log_file,
            maxBytes=1e+7,
            backupCount=5)

        formatter = logging.Formatter('%(asctime)s WD%(process)d:: \'CONTROLLER:\' - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Set up multiprocessing-safe logger
        logger = multiprocessing.get_logger()
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger


    def get_installed_browsers(self):
        """
        Function returns a set of browsers installed on the system. For windows it uses 
        'reg' library to read windows registry and fetch the installed browsers. 
        For Linux it uses a simple command of 'which'

        Function returns a set of browsers installed on the system. For windows it uses 
        'reg' library to read windows registry and fetch the installed browsers. 
        For Linux it uses a simple command of 'which'

        Args: None


        Returns: set of browsers installed on the system
        """
        browsers = set()
        if self.SYSTEM == 'Windows':
            import winreg as reg
            paths = [
                r"SOFTWARE\Clients\StartMenuInternet",
                r"SOFTWARE\WOW6432Node\Clients\StartMenuInternet"
                # For 32-bit apps on 64-bit system
            ]

            for path in paths:
                try:
                    # Open the registry key
                    key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, path)
                    i = 0
                    while True:
                        try:
                            # Enumerating subkeys
                            browser = reg.EnumKey(key, i)
                            if (browser[:13] == "Google Chrome"):
                                browsers.add("chrome")
                            elif browser[:14] == "Microsoft Edge":
                                browsers.add("edge")

                            i += 1
                        except WindowsError:
                            # If no more subkey, break the loop
                            break
                except WindowsError:
                    pass  # If key doesn't exist, move on to next one

        elif self.SYSTEM == 'Linux':
            command = 'which -a google-chrome microsoft-edge 2>/dev/null'
            output = subprocess.getoutput(command)
            for line in output.split('\n'):
                line = line.strip().replace('/usr/bin/', '')
                if line == 'google-chrome':
                    browsers.add('chrome')
                elif line == 'microsoft-edge':
                    browsers.add('edge')
                elif line == 'firefox':
                    browsers.add('firefox')
        return browsers


    def config_reader(self, conf_file_path="C:\\browsermon\\browsermon.conf"
    if platform.system() == "Windows" else "/opt/browsermon/browsermon.conf",
                    defaults=None):
        
        """
        Function reads the config file and returns a dictionary of options
        if the platform is windows then the default directory is C:\browsermon\brwosermon.conf
        otherwise for linux it is /opt/browsermon/browsermon.conf

        Args: conf_file_path: path to config file
        """

        def is_valid(value):
            pattern = r'^\d+[mhd]$'
            return re.match(pattern, value)

        options = {
            'browser',
            'mode',
            'schedule_window',
            'logdir',
            'logmode',
            'rotation',
            'backup_count'}

        if defaults is None:
            defaults = {'browser': 'all',
                        'mode': 'scheduled',
                        'schedule_window': '1m',
                        'logdir': 'C:\\browsermon\\history' if self.SYSTEM == "Windows" else '/opt/browsermon/history',
                        'logmode': 'csv',
                        'rotation': '1m',
                        'backup_count': '5'}

        try:
            config = configparser.ConfigParser()
            self.logger.info("Reading config file from path: %s", conf_file_path)
            config.read(conf_file_path)
        except Exception as config_init_exception:
            self.logger.warning(
                f"Exception caught during initialization: {config_init_exception}")
            return defaults

        config_values = {}

        for option in options:
            try:
                value = config.get('default', option)
                if not value:
                    raise ValueError(
                        self.logger.warning(f"Value for option '{option}' is empty"))
                if option == 'schedule_window' or option == 'rotation':
                    if not is_valid(value):
                        raise ValueError(
                            self.logger.warning(f"Value for option '{option}' is invalid"))
                if option == 'logmode':
                    if value not in {'csv', 'json'}:
                        raise ValueError(
                            self.logger.warning(f"Value for option '{option}' is invalid"))
                config_values[option] = value
            except (Exception, configparser.NoOptionError) as e:
                self.logger.warning(f"Exception caught for option '{option}': {e}")
                config_values[option] = defaults.get(option, None)

        self.logger.info(f"Options fetched from config file: {conf_file_path}")
        return config_values

    def run(self):
        launcher.set_multiprocessing_start_method()
        pid = os.getpid()
        self.logger.info(f"Main process id: {pid}")

        options = self.config_reader()
        self.logger.info(f"options fetched {options}")
        logdir = options['logdir']

        installed_browsers = self.get_installed_browsers()
        self.logger.info(f"Installed browsers: {installed_browsers}")


        self.launcherObj = launcher.Launcher(installed_browsers, self.logger, options)
        self.launcherObj.start()

        with handlers.Handler(self.logger, options['rotation'], f"{logdir}/browsermon_history.{options['logmode']}", options['backup_count']) as handler:
            while True:
                return_str = None
                self.logger.info("Controller waiting (blocked) on exit_feedback_queue")
                try: 
                    return_str = self.launcherObj.queue.get(timeout=15)
                    self.logger.info("Controller timed out waiting on exit_feedback_queue")
                    if (return_str == "edge exited"):
                        self.launcherObj.processes['edge'].join() #join before relaunching to avoid zombie processes
                        self.logger.info("exit_feedback_queue received enqueue from edge")
                        self.logger.error("edge reader has exited")
                        self.logger.info("Relaunching edge reader")
                        self.launcherObj.launch_reader("edge") #relaunch edge
                    elif (return_str == "chrome exited"):
                        self.launcherObj.processes['chrome'].join()
                        self.logger.info("exit_feedback_queue received enqueue from chrome")
                        self.logger.error("chrome reader has exited")
                        self.logger.info("Relaunching chrome reader")
                        self.launcherObj.launch_reader("chrome")
                    elif return_str != None:
                        self.logger.info("Recieved no relaunch feedback in queue")
                        self.logger.info("Exiting controller; breaking infinite loop in run")
                        time.sleep(2) #waiting for all child processes to exit before exiting controller
                        break
                except queue.Empty:
                    #checking if the processes are alive
                    self.logger.info("exit_feedback_queue is empty")
                    self.logger.info("Checking if child processes are still alive")
                    for processes in self.launcherObj.processes:
                        if not self.launcherObj.processes[processes].is_alive():
                            self.launcherObj.processes[processes].join() #join before relaunching the process 
                            self.logger.info("Process %s is not alive", processes)
                            self.logger.info("Relaunching process %s", processes)
                            self.launcherObj.launch_reader(processes)
                        else: 
                            self.logger.info("Process %s is alive, no need to relaunch", processes)
                            
