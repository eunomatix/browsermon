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
import datetime
import sys
import uuid
from collections import OrderedDict


class InvalidScheduleWindowFormat(Exception):
    """
    Custom exception for the InvalidScheduleWindowFormat
    """
    pass

def generate_uuid():
    """
    Generate a UUID
    :return: UUID
    """
    return str(uuid.uuid1())

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

    """
    Preparing entry to Write in json or CSV fromat.  
    :param Result: Gets result of Fetched Entries From Browser Database
    :param Metadata: Static metadata dictionary From Get static metadata funtion 
    :param Profile: Profile Link

    :return: Data ready for Writing

    """
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
    entry.update({"session_id": session_id, "referrer": referrer, "url": url,
        "title": title,
        "visit_time": visit_time_obj.strftime("%Y-%m-%d %H:%M:%S"),
        "visit_count": visit_count, })

    return entry
