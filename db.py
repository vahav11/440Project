import getpass
import mysql.connector
import config


# Remembers the password after the first time, so you are only asked
# once per run instead of on every database action.
_password = None


def get_password():
    global _password

    if _password is None:
        if config.DB_PASSWORD:
            _password = config.DB_PASSWORD
        else:
            _password = getpass.getpass("Enter your MySQL password: ")

    return _password


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=get_password(),
        database=config.DB_NAME
    )
