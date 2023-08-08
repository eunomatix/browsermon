import logging
import os
import platform

system = platform.system()
default_log_loc = None

if default_log_loc is None:
    if system == "Linux":
        default_log_loc = "/opt/browsermon"
    elif system == "Windows":
        default_log_loc = "C:\\browsermon"
    if not os.path.exists(default_log_loc):
        os.makedirs(default_log_loc)

log_file = os.path.join(default_log_loc, "browsermon.log")
log_format = "%(asctime)s WD%(process)d:: \'MICROSOFT-EDGE:\' - %(levelname)s %(message)s"  # noqa
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format=log_format)
logger = logging.getLogger(__name__)
