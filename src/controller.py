import configparser
import time
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
import platform
import launcher
import handlers

SYSTEM = platform.system()

if SYSTEM == "Windows":
    import wingreg as reg
config = configparser.ConfigParser()


defaults = {'browser': 'all',
            'mode': 'scheduled',
            'schedule_window': '1m',
            'logdir': '/home/appleconda/Documents/webdoggy/logs',
            'logmode': 'csv'}


def get_installed_browsers():
    """
    Function returns a set of browsers installed on the system.
    Args: None
    Returns: set of browsers installed on the system
    """
    browsers = set()
    if SYSTEM == 'Windows':
        paths = [
        r"SOFTWARE\Clients\StartMenuInternet",
        r"SOFTWARE\WOW6432Node\Clients\StartMenuInternet"  # For 32-bit apps on 64-bit system
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


def config_reader(conf_file_path='../browsermon.conf'):
    """
    Function reads the config file and returns a dictionary of options
    Args: conf_file_path: path to config file
    """

    config.read(conf_file_path)

    options = [
        'browser',
        'mode',
        'schedule_window',
        'logdir',
        'logmode',
        'rotation']

    config_values = {}

    for option in options:
        try:
            config_values[option] = config.get('default', option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            config_values[option] = defaults[option]

    return config_values


def run():
    """
    Function runs the controller, reads the config file
    initializes the logger
    and creates launcher object and calls the function start() on it.

    Args: None
    """
    options = config_reader()

    handler = RotatingFileHandler(
        "../browsermon.log",
        maxBytes=1e+7,
        backupCount=5)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - \'controller:\' - %(levelname)s - %(message)s',
        handlers=[handler])

    logger = logging.getLogger()
    logger.info("Options fetched from config file")

    cwd = os.getcwd()

    installed_browsers = get_installed_browsers()

    launcherObj = launcher.Launcher(installed_browsers, logger, options)
    launcherObj.start()


    with handlers.Handler(logger, options['rotation'], "../history/history.json", 5) as handler:
        time.sleep(300)
    


if __name__ == '__main__':
    run()

