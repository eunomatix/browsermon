import platform
import os
import subprocess
import threading


class Launcher:
    def __init__(self, installed_browsers, logger, options):
        self.installed_browsers = installed_browsers
        self.logger = logger
        self.options = options
        self.processes = []

    def monitor_subprocess(self, process, browser, mode,
                           scheduled_window, logdir, logmode):
        """
        monitor_subprocess function:
            monitors the subprocess launched by launch_reader function
            if the subprocess exits with error it relaunches the subprocess
            if the subprocess keeps exiting with error it only retries to launch it 5 times.
            'process' argument is the process object of the launched subprocess on which this function is monitoring
        Args: 
            process: process object of the launched subprocess
            browser: browser name
            mode: mode in which the reader should run
            scheduled_window: time window in which the reader should run
            logdir: directory where the log file should be stored
            logmode: mode in which the log file should be stored
        """

        pid = os.getpid()
        self.logger.debug(f'Monitoring thread pid: {pid}')
        count = 0
        while (1):
            process.wait()
            if process.returncode != 0 and count < 4:
                self.logger.error(
                    f'Subprocess: {browser}_reader.py exited with error')
                self.logger.debug(f'Retrieved code {process.returncode}')
                self.logger.info(
                    f"Relaunching the subprocess: {browser}_reader.py")
                process = subprocess.Popen(['python',
                                            f'{browser}_reader.py',
                                            mode,
                                            scheduled_window,
                                            logdir,
                                            logmode],
                                           stderr=subprocess.PIPE)
                self.logger.info(
                    "Relaunched the reader that exited with error")
                count += 1
            elif count > 3:
                self.logger.error(f'{browser}_reader.py keeps exiting')
                self.logger.info('Monitor thread is exiting')
                break
            else:
                self.logger.info(
                    "Subprocess completed with no errors; Monitor thread is exiting")
                break

    def launch_reader(self, browser, mode, scheduled_window, logdir, logmode):
        """
        Function launches the reader based on the browser provided

        Args:   browser: browser name
                mode: mode in which the reader should run
                scheduled_window: time window in which the reader should run
                logdir: directory where the log file should be stored
                logmode: mode in which the log file should be stored
        """
        self.logger.info(f"Invoking {browser}_reader.py")
        process = subprocess.Popen(['python',
                                    f'{browser}_reader.py',
                                    mode,
                                    scheduled_window,
                                    logdir,
                                    logmode],
                                   stderr=subprocess.PIPE)
        self.processes.append(process)
        self.logger.info(f"Invoked {browser}_reader.py")
        self.logger.info(f"Starting monitoring thread for {browser}_reader.py")
        monitorThread = threading.Thread(
            target=self.monitor_subprocess, args=(
                process, browser, mode, scheduled_window, logdir, logmode,))
        monitorThread.start()
        self.logger.info(f'Started monitoring thread for {browser}_reader.py')

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
                self.launch_reader(
                    browser,
                    self.options['mode'],
                    self.options['scheduled_window'],
                    self.options['logdir'],
                    self.options['logmode'])

        if self.options['browser'] in self.installed_browsers:
            self.launch_reader(
                self.options['browser'],
                self.options['mode'],
                self.options['schedule_window'],
                self.options['logdir'],
                self.options['logmode'])
        else:
            allowed_browsers = {'chrome', 'opera', 'firefox', 'edge', 'safari'}
            readers_list = self.options['browser'].split(",")
            if all(reader in allowed_browsers for reader in readers_list):
                readers_to_launch = [
                    reader for reader in readers_list if reader in self.installed_browsers]
                for browser in readers_to_launch:
                    self.launch_reader(
                        browser,
                        self.options['mode'],
                        self.options['scheduled_window'],
                        self.options['logdir'],
                        self.options['logmode'])

