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
        command = (
            'wmic datafile where "Extension=\'exe\' and '
            '(Filename like \'%\\Google\\Chrome\\%\' or '
            'Filename like \'%\\Mozilla Firefox\\%\' or '
            'Filename like \'%\\Microsoft\\Edge\\%\')" '
            'get Version, Manufacturer'
        )
        output = subprocess.getoutput(command)
        browsers = (line.split(',')[1].strip() if line.split(',')[1].strip(
        ) != 'google-chrome' else 'chrome' for line in output.split('\n') if line.strip() != '')
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


def config_reader(conf_file_path='/opt/browsermon/browsermon.conf'):
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
        f"{options['logdir']}/webdoggy_controller.log",
        maxBytes=1e+7,
        backupCount=5)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - \'controller:\' - %(levelname)s - %(message)s',
        handlers=[handler])

    logger = logging.getLogger()
    logger.info("Options fetched from config file")

    cwd = os.getcwd()
    file_to_rotate = '/home/appleconda/Documents/Files/webdoggy/file.json'

    installed_browsers = get_installed_browsers()

    launcherObj = launcher.Launcher(installed_browsers, logger, options)
    launcherObj.start()

    with handlers.Handler(logger, options['rotation'], f"{cwd}/file.json", 5) as handler:
        logger.info("Creating scheduled job")
        time.sleep(300)
    


if __name__ == '__main__':
    run()

