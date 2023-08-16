import os 
import re
from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler

class Handler:
    def __init__(self, logger, rotation, file_path, backup_count):

        self.logger = logger
        self.rotation = rotation
        self.file_path = file_path
        self.backup_count = int(backup_count)
        self.scheduler = BackgroundScheduler()

    
    def rollover(self):
        """ 
        Function: rollover()
            Descirption: This function is for rotationThreshold of history log files that readers generates; how it works is that 
            if will rename the current history log files that all readers are writing to and create a new file with old name 
            history log files. 

        Args: None
            
        """
        MIN_THRESHOLD = 0
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == MIN_THRESHOLD:
            return
        rotated_files = [self.file_path] + [self.file_path + '.{}'.format(str(i)) for i in range(1, self.backup_count + 1)]

        if os.path.exists(rotated_files[-1]):
            os.remove(rotated_files[-1])

        for i in range(len(rotated_files) - 1, 0, -1):
            source_file = rotated_files[i - 1]
            destination_file = rotated_files[i]
            
            if os.path.exists(source_file):
                os.rename(source_file, destination_file)

        open(self.file_path, 'a').close()

    def get_scheduler_info(self, scheduler, logger):
        """ 
        get_scheduler_info(, scheduler, logger) 
        Description:
            This function is to log all the details about the apscheduler.backgroundScheduler

        Args: 
            scheduler: (the object of the apscheduler that you wish to log information about
            
            logger: the objecct of the logging module that is responsible for logging into the log file. 
        """

        logger.info("Scheduler information:")
        # Iterate over all jobs in the scheduler
        for job in scheduler.get_jobs():
            # Retrieve trigger information
            if isinstance(job.trigger, CronTrigger):
                cron_expression = job.trigger.fields
                logger.info(f"Job Trigger Type: CronTrigger")
                #logger.info(f"Cron Expression: {cron_expression}")
                next_run_time = job.next_run_time  # Use job's next_run_time attribute
                logger.info(f"Next Run Time: {next_run_time}")
            else:
                logger.info(f"Job Trigger Type: {type(job.trigger).__name__}")
                next_run_time = job.next_run_time  # Use job's next_run_time attribute
                logger.info(f"Next Run Time: {next_run_time}")


    def schedule_background_job(self):
        """ 
        schedule_background_job()
        Description: 
            This function is to schedule the rollover job for rotating files. 
            This function uses apscheduler library in python to schedule the job. 

        Args: None
        """
        # Extract the numeric value and unit from the input string
        match = re.match(r'^(\d+)([mhd])$', self.rotation)
        if not match:
            raise ValueError("Invalid interval format")

        value = int(match.group(1))
        unit = match.group(2)

        # Map the unit to the appropriate cron expression
        if unit == 'm':
            cron_expr = f"*/{value} * * * *"
        elif unit == 'h':
            cron_expr = f"0 */{value} * * *"
        elif unit == 'd':
            cron_expr = f"0 0 */{value} * *"
        else:
            raise ValueError("Invalid interval unit")

        self.scheduler.add_job(self.rollover, trigger=CronTrigger.from_crontab(cron_expr))
        self.scheduler.start() 
                
    def __enter__(self):   
        self.logger.info("Handler class invoked")
        self.logger.info(f"Running the scheduled job: rollover (funciton) for duration: {self.rotation}")
        self.schedule_background_job()
        self.get_scheduler_info(self.scheduler, self.logger)

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info("Cleanup of Handler class")
        self.scheduler.shutdown()
        self.scheduler.remove_all_jobs()

