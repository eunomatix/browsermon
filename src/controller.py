import re
import logging
import platform
import subprocess
import configparser
import multiprocessing as mp
from logging.handlers import RotatingFileHandler

import handlers
import launcher

SYSTEM = platform.system()

if SYSTEM == "Windows":
    import winreg as reg


def get_installed_browsers():
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
    if SYSTEM == 'Windows':
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
                        elif browser[:7] == "Firefox":
                            browsers.add("firefox")

                        i += 1
                    except WindowsError:
                        # If no more subkey, break the loop
                        break
            except WindowsError:
                pass  # If key doesn't exist, move on to next one

    elif SYSTEM == 'Linux':
        command = 'which -a google-chrome firefox chromium-browser microsoft-edge brave-browser 2>/dev/null'
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


def config_reader(logger, conf_file_path="C:\\browsermon\\browsermon.conf"
if SYSTEM == "Windows" else "/opt/browsermon/browsermon.conf",
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
        'deletion'}

    if defaults is None:
        defaults = {'browser': 'all',
                    'mode': 'scheduled',
                    'schedule_window': '1m',
                    'logdir': 'C:\\browsermon\\history' if SYSTEM == "Windows" else '/opt/browsermon/history',
                    'logmode': 'csv',
                    'rotation': '1m',
                    'deletion': '1w'}

    try:
        config = configparser.ConfigParser()
        logger.info("Reading config file from path: %s", conf_file_path)
        config.read(conf_file_path)
    except Exception as config_init_exception:
        logger.warning(
            f"Exception caught during initialization: {config_init_exception}")
        return defaults

    config_values = {}

    for option in options:
        try:
            value = config.get('default', option)
            if not value:
                raise ValueError(
                    logger.warning(f"Value for option '{option}' is empty"))
            if option == 'schedule_window' or option == 'rotation' or option == 'deletion':
                if not is_valid(value):
                    raise ValueError(
                        logger.warning(f"Value for option '{option}' is invalid"))
            if option == 'logmode':
                if value not in ['csv', 'json']:
                    raise ValueError(
                        logger.warning(f"Value for option '{option}' is invalid"))
            config_values[option] = value
        except (Exception, configparser.NoOptionError) as e:
            logger.warning(f"Exception caught for option '{option}': {e}")
            config_values[option] = defaults.get(option, None)

    logger.info(f"Options fetched from config file: {conf_file_path}")
    return config_values


def init_logger(SYSTEM):
    """
    Function:
        The function initializes the logger object on the log file if the system is windows it will attach to
        C:\\browsermon\\browsermon.log
        otherwise for linux
        /opt/browsermon/browsermon.log
    Args:
        SYSTEM
            Which could be either Windows or Linux
            Initialize SYSTEM with os.platform()
    """

    if SYSTEM == "Windows":
        handler = RotatingFileHandler(
            "C:\\browsermon\\browsermon.log",
            maxBytes=1e+7,
            backupCount=5)
    elif SYSTEM == "Linux":
        handler = RotatingFileHandler(
            "/opt/browsermon/browsermon.log",
            maxBytes=1e+7,
            backupCount=5)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s WD%(process)d:: \'CONTROLLER:\' - %(levelname)s - %(message)s',
        handlers=[handler])

    logger = logging.getLogger()
    return logger


def run():
    """
    Function: Is the driver function of controller.
        Step 1: Initialize the logger by calling init_logger the Logger object returned by the function will be stored
                in "logger" variable
        Step 2: Fetch options from configuration file by called 'config_reader'
        Step 3: Get set of installed browsers by calling 'get_installed_browser()' function
        step 4: Create Launcher object
                    The Launcher object is passed
                        -> set of installed browsers
                        -> logger object
                        -> options fetched from configuration file
                    The Launcher class is responsible for launching readers
        Step 5: Create Handler object through context Manager to ensure proper shutdown of this scheduled operation
                    The handler class's constructor takes the following
                        -> logger object
                        -> file to rotate with it's extension either csv or json
        Step 6: Wait on LauncherObject's queue (which is a multirpocessing.queue), The reader will write in this queue
                it's identity when exiting so controller can relaunch it again.

    Args: None
    """

    logger = init_logger(SYSTEM)

    options = config_reader(logger)

    logdir = options['logdir']
    installed_browsers = get_installed_browsers()

    launcherObj = launcher.Launcher(installed_browsers, logger, options)
    launcherObj.start()

    with handlers.Handler(logger, options['rotation'],
                          f"{logdir}/browsermon_history.{options['logmode']}",
                          5) as handler:
        while True:
            logger.info("Controller waiting (blocked) on exit_feedback_queue")
            return_str = launcherObj.queue.get()
            if (return_str == "edge Exited"):
                logger.info("exit_feedback_queue received enqueue from edge")
                logger.error("edge reader has exited")
                logger.info("Relaunching edge reader")
                launcherObj.launch_reader("edge")

            elif (return_str == "chrome Exited"):
                logger.info("exit_feedback_queue received enqueue from chrome")
                logger.error("chrome reader has exited")
                logger.info("Relaunching chrome reader")
                launcherObj.launch_reader("chrome")


if __name__ == '__main__':
    run()
