import multiprocessing as mp 

from edge_reader import main as edge_reader_main
from chrome_reader import main as chrome_reader_main

def set_multiprocessing_start_method():
    try:
        mp.set_start_method('spawn')
    except RuntimeError as e:
        pass

class Launcher:
    def __init__(self, installed_browsers, logger, options):
        self.installed_browsers = installed_browsers
        self.logger = logger
        self.options = options
        self.processes = {}
        self.queue = mp.Queue()
        

    def launch_reader(self, browser):
        """
        Function launches the reader based on the browser provided

        Args:   browser: browser name
                mode: mode in which the reader should run
                scheduled_window: time window in which the reader should run
                logdir: directory where the log file should be stored
                logmode: mode in which the log file should be stored
        """

        if browser == 'edge':
            self.logger.info("Invoking MICORSOFOT EDGE reader")
            process_edge = mp.Process(target=edge_reader_main, args=(self.queue, self.options['logdir'], self.options['logmode'], self.options['mode'], self.options['schedule_window']))
            process_edge.start()
            print("Launched reader with pid ", process_edge.pid)
            self.logger.info("Invoked MICOROSOFT EDGE reader; PID: " + str(process_edge.pid))
            self.processes['edge'] = process_edge
        if browser == 'chrome':
            import chrome_reader
            self.logger.info("Invoking CHROME reader")
            process_chrome = mp.Process(target=chrome_reader_main, args=(self.queue, self.options['logdir'], self.options['logmode'], self.options['mode'], self.options['schedule_window']))
            process_chrome.start()
            print("Launched reader with pid ", process_chrome.pid)
            self.logger.info("Invoked CHROME reader; PID: " + str(process_chrome.pid))
            self.processes['chrome'] = process_chrome


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
