import configparser
import logging
import platform
import re
import subprocess
import time
from logging.handlers import RotatingFileHandler

import handlers
import launcher

SYSTEM = platform.system()

if SYSTEM == "Windows":
    import winreg as reg


class ExcludeTimeZoneFilter(logging.Filter):
    def filter(self, record):
        # Exclude log records with the specific message about the timezone configuration
        if record.getMessage() == "/etc/localtime is a symlink to: Asia/Karachi":
            return False
        return True


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
        logger.warn(
            f"Exception caught during initialization: {config_init_exception}")
        return defaults

    config_values = {}

    for option in options:
        try:
            value = config.get('default', option)
            if not value:
                raise ValueError(
                    logger.warn(f"Value for option '{option}' is empty"))
            if option == 'schedule_window' or option == 'rotation' or option == 'deletion':
                if not is_valid(value):
                    raise ValueError(
                        logger.warn(f"Value for option '{option}' is invalid"))
            if option == 'logmode':
                if value not in ['csv', 'json']:
                    raise ValueError(
                        logger.warn(f"Value for option '{option}' is invalid"))
            config_values[option] = value
        except (Exception, configparser.NoOptionError) as e:
            logger.warn(f"Exception caught for option '{option}': {e}")
            config_values[option] = defaults.get(option, None)

    logger.info("Options fetched from config file")
    return config_values


def init_logger(SYSTEM):
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
    Function runs the controller, reads the config file
    initializes the logger
    and creates launcher object and calls the function start() on it.
    The launcher class is responsible for launching the readers, The launcher class is initialized with following parameters
        installed browsers (set of names of installed browsers)
        logging object (The logging module for which launcher will log) 
        options (The options that are read from the conf file are also to be send to launcher) 
    The launcher class is responsible for launching the readers, The launcher class is initialized with following parameters
        installed browsers (set of names of installed browsers)
        logging object (The logging module for which launcher will log) 
        options (The options that are read from the conf file are also to be send to launcher) 

    Args: None
    """

    logger = init_logger(SYSTEM)

    options = config_reader(logger)
    print(options)
    logdir = options['logdir']
    installed_browsers = get_installed_browsers()

    launcherObj = launcher.Launcher(installed_browsers, logger, options)
    launcherObj.start()

    with handlers.Handler(logger, options['rotation'],
                          f"{logdir}/browsermon_history.{options['logmode']}",
                          5) as handler:
        time.sleep(300)


if __name__ == '__main__':
    run()
