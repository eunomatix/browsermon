# ****************************************************************************
# **
# ** Copyright (C) 2023 EUNOMATIX
# ** This program is free software: you can redistribute it and/or modify
# ** it under the terms of the GNU General Public License as published by
# ** the Free Software Foundation, either version 3 of the License, or
# ** any later version.
# **
# ** This program is distributed in the hope that it will be useful,
# ** but WITHOUT ANY WARRANTY; without even the implied warranty of
# ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# ** GNU General Public License for more details.
# **
# ** You should have received a copy of the GNU General Public License
# ** along with this program. If not, see <https://www.gnu.org/licenses/>.
# **
# ** Contact: info@eunomatix.com
# **
# **************************************************************************/
import multiprocessing as mp 

from readers.edge_reader import main as edge_reader_main
from readers.chrome_reader import main as chrome_reader_main
from readers.firefox_reader import main as firefox_reader_main

def set_multiprocessing_start_method():
    try:
        mp.set_start_method('spawn')
    except RuntimeError:
        pass

class Launcher:
    def __init__(self, installed_browsers, logger, options):
        self.installed_browsers = installed_browsers
        self.logger = logger
        self.options = options
        self.processes = {}
        self.queue = mp.Queue()
        self.shared_lock = mp.Lock()
        self.shared_lock.acquire(block=True)

    def launch_reader(self, browser):
        """
        Function launches the reader based on the browser provided

        Args:   browser: browser name
                mode: mode in which the reader should run
                scheduled_window: time window in which the reader should run
                logdir: directory where the log file should be stored
                logmode: mode in which the log file should be stored
        """

        self.logger.info("Controller: accquiring Lock")
        if browser == 'edge':
            self.logger.info("Invoking MICORSOFOT EDGE reader")
            process_edge = mp.Process(target=edge_reader_main, args=(self.queue, self.shared_lock, self.options['logdir'], self.options['logmode'], self.options['mode'], self.options['schedule_window']))
            process_edge.start()
            print("Launched reader with pid ", process_edge.pid)
            self.logger.info("Invoked MICOROSOFT EDGE reader; PID: " + str(process_edge.pid))
            self.processes['edge'] = process_edge
        if browser == 'chrome':
            self.logger.info("Invoking CHROME reader")
            process_chrome = mp.Process(target=chrome_reader_main, args=(self.queue, self.shared_lock, self.options['logdir'], self.options['logmode'], self.options['mode'], self.options['schedule_window']))
            process_chrome.start()
            print("Launched reader with pid ", process_chrome.pid)
            self.logger.info("Invoked CHROME reader; PID: " + str(process_chrome.pid))
            self.processes['chrome'] = process_chrome
        if browser == 'firefox':
            self.logger.info("Invoking FIREFOX reader")
            process_firefox = mp.Process(target=firefox_reader_main, args=(self.queue, self.shared_lock, self.options['logdir'], self.options['logmode'], self.options['mode'], self.options['schedule_window']))
            process_firefox.start()
            print("Launched reader with pid ", process_firefox.pid)
            self.logger.info("Invoked FIREFOX reader; PID: " + str(process_firefox.pid))
            self.processes['firefox'] = process_firefox



    def start(self):
        """
        start function:
            starts the reader based on the options provided
            It validates the browser option whether it's all, single or multiple
            It launches the reader based on the browser option provided

        Args: None
        """
        if self.options['browser'] == 'all':
            for browser in self.installed_browsers:
                self.launch_reader(browser)

        if self.options['browser'] in self.installed_browsers:
            self.launch_reader(self.options['browser'])
        else:
            allowed_browsers = {'chrome', 'edge', 'firefox'}
            readers_list = self.options['browser'].split(",")
            if all(reader in allowed_browsers for reader in readers_list):
                readers_to_launch = [
                    reader for reader in readers_list if reader in self.installed_browsers]
                for browser in readers_to_launch:
                    self.launch_reader(browser)
