import os
import platform


default_log_loc = None

if default_log_loc is None:
    if platform.system() == "Linux":
        default_log_loc = "/opt/browsermon"
    elif platform.system() == "Windows":
        default_log_loc = "C:\\browsermon"
    if not os.path.exists(default_log_loc):
        os.makedirs(default_log_loc)