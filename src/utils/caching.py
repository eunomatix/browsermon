""""/****************************************************************************
 **
 ** Copyright (C) 2023 EUNOMATIX
 ** This program is free software: you can redistribute it and/or modify
 ** it under the terms of the GNU General Public License as published by
 ** the Free Software Foundation, either version 3 of the License, or
 ** any later version.
 **
 ** This program is distributed in the hope that it will be useful,
 ** but WITHOUT ANY WARRANTY; without even the implied warranty of
 ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 ** GNU General Public License for more details.
 **
 ** You should have received a copy of the GNU General Public License
 ** along with this program. If not, see <https://www.gnu.org/licenses/>.
 **
 ** Contact: info@eunomatix.com
 **
 **************************************************************************/
"""
import json
import os

from utils import logger
from utils.encryption import encrypt_data, decrypt_data


def write_cache_file(cache_file, encryption_key, cache):
    """
    Write the cache file with the last visit times in encrypted format.
    :return: None
    """
    # Serialize cache dictionary to bytes using orjson
    encrypted_data = encrypt_data(json.dumps(cache), encryption_key)

    with open(cache_file, "wb") as file:
        file.write(encrypted_data)

    logger.info("Cache file written with last visit times", extra={"log_id": 8004})


def read_cache_file(cache_file, encryption_key):
    """
    Read the cache file and decrypt the last visit times.
    :return: None
    """
    cache = {}

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as file:
            encrypted_data = file.read()

        decrypted_data = decrypt_data(encrypted_data, encryption_key)

        cache = json.loads(decrypted_data)

        logger.info("Cache file read and last visit times decrypted",
                    extra={"log_id": 1002})

    return cache
