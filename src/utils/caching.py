import json
import os

from utils.common import write_logs
from utils.encryption import encrypt_data, decrypt_data


def write_cache_file(cache_file, encryption_key, last_visit_times):
    """
    Write the cache file with the last visit times in encrypted format.
    :return: None
    """
    # Serialize last_visit_times dictionary to bytes using orjson
    encrypted_data = encrypt_data(json.dumps(last_visit_times), encryption_key)

    with open(cache_file, "wb") as file:
        file.write(encrypted_data)

    write_logs("info", "Cache file written with last visit times")


def read_cache_file(cache_file, encryption_key):
    """
    Read the cache file and decrypt the last visit times.
    :return: None
    """
    last_visit_times = {}

    if os.path.exists(cache_file):
        with open(cache_file, "rb") as file:
            encrypted_data = file.read()

        decrypted_data = decrypt_data(encrypted_data, encryption_key)

        last_visit_times = json.loads(decrypted_data)

        write_logs("info", "Cache file read and last visit times decrypted")

    return last_visit_times
