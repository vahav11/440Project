import getpass
import mysql.connector
import config


# remember it so we only ask once per run
_password = None


def get_password():
    global _password

    # not None, because an empty answer would get cached and then every
    # connection fails with access denied
    if not _password:
        if config.DB_PASSWORD:
            _password = config.DB_PASSWORD
        else:
            print("(typing is hidden, just type it and press enter)")
            while not _password:
                _password = getpass.getpass("MySQL password: ").strip()

    return _password


def get_connection():
    return mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=get_password(),
        database=config.DB_NAME
    )
