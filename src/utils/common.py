import datetime
import logging
import os
import sys
from collections import OrderedDict

from src.utils import default_log_loc


def write_logs(level, message):
    """
    Write logs to the browsermon.log file
    :param level: Log level (info, error, warning)
    :param message: Log message
    :return: None
    """

    log_file = os.path.join(default_log_loc, "browsermon.log")
    log_format = "%(asctime)s WD%(process)d:: \'MICROSOFT-EDGE:\' - %(levelname)s %(message)s"  # noqa
    logging.basicConfig(filename=log_file, level=logging.INFO,
                        format=log_format)

    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)
    elif level == "warning" or level == "warn":
        logging.warning(message)


class InvalidScheduleWindowFormat(Exception):
    """
    Custom exception for the InvalidScheduleWindowFormat
    """
    pass


def parse_schedule_window(window):
    """
    Parse the schedule window argument into seconds.
    :param window: Schedule window argument (e.g., 1m, 1h, 1d)
    :return: Schedule window in seconds
    """
    try:
        if window[-1] == "m":
            return int(window[:-1]) * 60
        elif window[-1] == "h":
            return int(window[:-1]) * 3600
        elif window[-1] == "d":
            return int(window[:-1]) * 86400
        else:
            raise InvalidScheduleWindowFormat
    except InvalidScheduleWindowFormat:
        print(
            "Invalid schedule window format. Please use the valid format (e.g., 1m, 1h, 1d)")  # noqa
        sys.exit(1)


def prepare_entry(result, metadata, profile):
    session_id = result[0]
    referrer = result[1]
    url = result[2]
    title = result[3]
    visit_time = result[4]
    visit_count = result[5]

    visit_time_obj = datetime.datetime(1601, 1, 1) + datetime.timedelta(
        microseconds=visit_time)

    # Create an OrderedDict to maintain the order of keys
    entry = OrderedDict()

    # Add metadata and profile information at the beginning of the entry
    entry.update(metadata)
    entry.update(profile)

    # Add other entry information
    entry.update({
        "session_id": session_id,
        "referrer": referrer,
        "url": url,
        "title": title,
        "visit_time": visit_time_obj.strftime("%Y-%m-%d %H:%M:%S"),
        "visit_count": visit_count,
    })

    return entry
