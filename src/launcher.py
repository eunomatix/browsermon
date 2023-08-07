import multiprocessing as mp 


class Launcher:
    def __init__(self, installed_browsers, logger, options):
        self.installed_browsers = installed_browsers
        self.logger = logger
        self.options = options
        self.processes = []
        self.queue = None
        mp.set_start_method('spawn')
        

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
            import edge_reader
            self.queue = mp.Queue()
            p = mp.Process(target=edge_reader.main, args=(self.queue, self.options['logdir'], self.options['logmode'], self.options['mode'], self.options['schedule_window']))
            p.start()
            print("Launched reader with pid ", p.pid)
            self.logger.info("Invoked MICOROSOFT EDGE reader; PID: " + str(p.pid))
            self.processes.append(p)
        if browser == 'chrome':
            import chrome_reader
            self.logger.info("Invoking CHROME reader")
            self.queue = mp.Queue()
            p = mp.Process(target=chrome_reader.main, args=(self.queue, self.options['logdir'], self.options['logmode'], self.options['mode'], self.options['schedule_window']))
            p.start()
            print("Launched reader with pid ", p.pid)
            self.logger.info("Invoked CHROME reader; PID: " + str(p.pid))
            self.processes.append(p)


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
