import logging
import os
import platform

# Define default log locations using a dictionary
DEFAULT_LOG_LOCATIONS = {"Linux": "/opt/browsermon",
    "Windows": "C:\\browsermon"}

# Determine system and set default log location
system = platform.system()
default_log_loc = DEFAULT_LOG_LOCATIONS.get(system)

if default_log_loc and not os.path.exists(default_log_loc):
    os.makedirs(default_log_loc)

log_file = os.path.join(default_log_loc, "browsermon.log")
log_format = "%(asctime)s BM%(log_id)s:: EDGE-READER: %(levelname)s %(message)s"


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if not hasattr(record, 'log_code'):
            record.log_code = ''  # Set an empty log code if not present
        return super().format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set the logger level to INFO

formatter = CustomFormatter(log_format)

# Set up logger and handler using context managers
with open(log_file, 'a'):
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
