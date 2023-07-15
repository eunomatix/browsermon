import configparser
import time
import os
import subprocess
import threading 
import handlers
import launcher
import platform

SYSTEM = platform.system()

config = configparser.ConfigParser() 
config.read('webdoggy.conf')

logdir = config.get('default', 'logdir')
logger = handlers.init_logger(logdir)

defaults = {'browser': 'all', 
            'mode': 'scheduled', 
            'schedule_window': '1m', 
            'logdir': '/home/appleconda/Documents/webdoggy/logs', 
            'logmode': 'csv'}


def get_installed_browsers():
    #<Summary>
    # get_installed_browsers function:
    #   returns a set of installed browsers on the system works on windows and linux
    #</Summary> 

    if SYSTEM == 'Windows':
        command = 'wmic datafile where "Extension=\'exe\' and (Filename like \'%\\Google\\Chrome\\%\' or Filename like \'%\\Mozilla Firefox\\%\' or Filename like \'%\\Microsoft\\Edge\\%\')" get Version, Manufacturer'
        output = subprocess.getoutput(command)
        browsers = {line.split(',')[1].strip() if line.split(',')[1].strip() != 'google-chrome' else 'chrome' for line in output.split('\n') if line.strip() != ''}
    elif SYSTEM == 'Linux':
        command = 'which -a google-chrome firefox chromium-browser microsoft-edge brave-browser 2>/dev/null'
        output = subprocess.getoutput(command)
        browsers = {line.strip().replace('/usr/bin/', '') if line.strip().replace('/usr/bin/', '') != 'google-chrome' else 'chrome' if 'google-chrome' in line else 'edge' if 'microsoft-edge' in line else line for line in output.split('\n') if line.strip() != ''}
    else:
        browsers = set()

    return browsers


def config_reader(): 
    #<Summary> 
    # config_reader function: 
    #   reads the config file and returns the options
    #</Summary>
    logger.info('Reading config file')

    try: 
        browser = config.get('default', 'browser')
        mode = config.get('default', 'mode')
        scheduled_window = config.get('default', 'schedule_window')
        logdir = config.get('default', 'logdir')
        logmode = config.get('default', 'logmode')
        rotation = config.get('default', 'rotation')

    except configparser.NoSectionError or configparser.NoOptionError:
        logger.warn("No section or option found")
        logger.info("Setting default value")


    logger.debug(f'Browser: {browser}')
    logger.debug(f'mode: {mode}')
    logger.debug(f'scheduled: {scheduled_window}')
    logger.debug(f'logdir: {logdir}')
    logger.debug(f'logmode: {logmode}')
    logger.debug(f'rotation:{rotation}')

    logger.info("Reading config file completed, all options fetched")

    options = {'browser': browser, 'mode' : mode, 'scheduled_window': scheduled_window, 'logdir': logdir, 'logmode': logmode, 'rotation': rotation}
    return options


def run():
    options = config_reader()
    cwd = os.getcwd()
    file_to_rotate = '/home/appleconda/Documents/Files/webdoggy/file.json'

    installed_browsers = get_installed_browsers()

    Launcher = launcher.launcher(installed_browsers, logger, options)
    Launcher.start()    

    handlers.set_schedule_job(options['rotation'], f"{cwd}/rollover.py {file_to_rotate} 5", logger)




if __name__ == '__main__': 
    try: 
        run()
        time.sleep(300)
    except KeyboardInterrupt:
        logger.info('Keyboard Interrupt')
        handlers.clean_scheduled_jobs(logger)
        logger.info("exiting program")
        exit(0)



