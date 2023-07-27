import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def gen_fernet_key(passcode: str) -> bytes:
    assert isinstance(passcode, str)

    # Convert the password to bytes
    passcode = passcode.encode('utf-8')

    # Use a fixed salt value (you can choose any constant value here)
    salt = b'BrowserMon'

    # Use PBKDF2 to derive the key from the password and salt
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32,
                     # Fernet key size is 32 bytes
                     salt=salt, iterations=100000,
                     # Adjust the number of iterations as needed for security
                     backend=default_backend())

    key = base64.urlsafe_b64encode(kdf.derive(passcode))
    return key


def encrypt_data(data, key):
    """
    Encrypt the data using AES encryption with the key.
    :param data: Data to be encrypted
    :param key: Encryption key
    :return: Encrypted data
    """
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(data.encode())
    return encrypted_data


def decrypt_data(data, key):
    """
    Decrypt the data using AES encryption with the key.
    :param data: Data to be decrypted
    :param key: Decryption key
    :return: Decrypted data
    """
    cipher = Fernet(key)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data.decode()
