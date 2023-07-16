import logging
import os
import sys
import platform
import datetime
from logging.handlers import RotatingFileHandler
from datetime import datetime

SYSTEM = platform.system()

if SYSTEM == 'Windows':
    import win32com.client


class Handlers:
    def __init__(self, logger, rotation, path_of_script, Args):
        self.logger = logger
        self.rotation = rotation
        self.path_of_script = path_of_script
        self.Args = Args

    def convert_to_cron_syntax(self, time_string):
        unit = time_string[-1]   # get the time unit: h, d, m
        value = int(time_string[:-1])  # get the numerical value

        if unit == 'm':
            if value != 1:
                self.logger.error("Cron can't handle minutes greater than 59. Please provide valid input.")
                return None
            cron_syntax = '* * * * *'
        elif unit == 'h':
            if value < 0 or value > 23:
                self.logger.error("Cron can't handle hours outside the range 0-23. Please provide valid input.")
                return None
            cron_syntax = f'0 {value} * * *'
        elif unit == 'd':
            if value < 1 or value > 31:
                self.logger.error("Cron can't handle days outside the range 1-31. Please provide valid input.")
                return None
            cron_syntax = f'0 0 {value} * *'
        else:
            self.logger.error("Invalid time format. Please provide valid input.")
            return None

        return cron_syntax

    def set_schedule_job(self, rotation, path_of_script, Args):
        python_path = sys.executable
        if (SYSTEM == 'Linux'):
            self.logger.info("System identified as Linux")
            cron_command = f"{python_path} {path_of_script} {Args} >> /tmp/cron_job.log 2>&1"

    #        cron_schedule = "*/1 * * * *"

            cron_schedule = self.convert_to_cron_syntax(rotation)
            logging.debug(f"cron_schedule: {cron_schedule}")

            temp_cron_file = "/tmp/temp_cron"

            with open(temp_cron_file, 'w') as file:
                file.write(cron_schedule + ' ' + cron_command + '\n')

            os.system('crontab {}'.format(temp_cron_file))

            os.remove(temp_cron_file)
            self.logger.debug(f"Cron Command: {cron_schedule} {cron_command}")
            self.logger.info("Cron job added")

        elif (SYSTEM == 'Windows'):
            self.logger.info("System identified as Windows")

            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()

            self.logger.info("Connected to scheduler")

            root_folder = scheduler.GetFolder('\\')
            task_def = scheduler.NewTask(0)

            # Create trigger
            start_time = datetime.datetime.now()

            if rotation.endswith('h'):
                hours = int(rotation[:-1])
                TASK_TRIGGER_DAILY = 2  # 2 means the task is meant to run daily
                trigger = task_def.Triggers.Create(TASK_TRIGGER_DAILY)
                trigger.StartBoundary = start_time.isoformat()
                trigger.DaysInterval = 1
                trigger.Repetition.Duration = ""
                # Convert hours to minutes
                trigger.Repetition.Interval = f"PT{hours * 60}M"

            elif rotation.endswith('d'):
                days = int(rotation[:-1])
                TASK_TRIGGER_WEEKLY = 3  # 3 means the task is meant to run weekly
                trigger = task_def.Triggers.Create(TASK_TRIGGER_WEEKLY)
                trigger.StartBoundary = start_time.isoformat()
                trigger.DaysOfWeek = 0x7F  # Run on all days of the week
                trigger.WeeksInterval = days
                trigger.Repetition.Duration = ""
                trigger.Repetition.Interval = "PT24H"  # 24 hours interval

            elif rotation.endswith('m'):
                minutes = int(rotation[:-1])
                TASK_TRIGGER_DAILY = 2  # 2 means the task is meant to run daily
                trigger = task_def.Triggers.Create(TASK_TRIGGER_DAILY)
                trigger.StartBoundary = start_time.isoformat()
                trigger.DaysInterval = 1
                trigger.Repetition.Duration = ""
                trigger.Repetition.Interval = f"PT{minutes}M"

            else:
                raise ValueError("Invalid time format")

            self.logger.info("Trigger created")
            self.logger.debug(
                f"Trigger start boundary set to {start_time.isoformat()}")
            self.logger.debug(
                f"Trigger repetition interval set to {trigger.Repetition.Interval}")

            # Create action
            TASK_ACTION_EXEC = 0  # means that the action is an executable action
            action = task_def.Actions.Create(TASK_ACTION_EXEC)
            action.ID = 'Run webdoggy rotation task'
            action.Path = python_path  # Use the Python executable from the current environment
            action.Arguments = path_of_script  # Replace with the path to your Python script

            # Set parameters
            task_def.RegistrationInfo.Description = 'Test Task'
            task_def.Settings.Enabled = True
            task_def.Settings.StopIfGoingOnBatteries = False

            # Register task
            # If task already exists, it will be updated
            TASK_CREATE_OR_UPDATE = 6
            TASK_LOGON_NONE = 0
            root_folder.RegisterTaskDefinition(
                'webdoggy rotation task',
                task_def,
                TASK_CREATE_OR_UPDATE,
                '',  # No user
                '',  # No password
                TASK_LOGON_NONE)

            self.logger.info("Task registered")
    
    def __enter__(self):
        self.set_schedule_job(self.rotation, self.path_of_script, self.Args)
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        if SYSTEM == 'Linux':
            self.logger.info("Removing entries in crontab")
            temp_cron_file = '/tmp/temp_cron.backup'
            os.system("crontab -l > {}".format(temp_cron_file))
            self.logger.info(f"Creating backup of crontab in {temp_cron_file}")
            os.system('crontab -r')
            self.logger.info("Removed entries in crontab")
        elif SYSTEM == 'Windows':
            self.logger.info("Removing scheduled tasks")
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            root_folder = scheduler.GetFolder('\\')
            root_folder.DeleteTask('webdoggy rotation task', 0)
            self.logger.info("Removed scheduled tasks")
