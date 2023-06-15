import json
import os


def read_config(file_name: str = "config.json") -> dict:
    with open(file_name, 'r') as json_file:
        cfg = json.load(json_file)
    return cfg


development_key = 'dev'
production_key = 'prod'
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
private_key_file = f'{project_dir}/private.pem'
public_key_file = f'{project_dir}/public.pem'


class Config(object):
    """Base config, uses staging database server."""
    # main config
    SECRET_KEY = 'my_precious'
    SECURITY_PASSWORD_SALT = 'my_precious_two'
    DEBUG = False
    TESTING = False
    DB_SERVER = '0.0.0.0'
    PORT = 5000
    DATABASE_URL = "sqlite:///./test.db"
    SQL_ECHO = True
    LOG_FOLDER = './logs'
    PRIVATE_KEY = open(private_key_file).read()
    PUBLIC_KEY = open(public_key_file).read()
    REQUEST_MAX_SIZE = 1000000  # 1mb
    REQUEST_TIMEOUT = 15  # 15s

    # mail settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = os.environ.get('APP_MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('APP_MAIL_PASSWORD', '')

    # mail accounts
    MAIL_DEFAULT_SENDER = 'from@example.com'

    def __init__(self, mode: str = 'default'):
        mode = mode.lower()
        if mode == 'production':
            """Uses production database server."""
            self.DB_SERVER = '0.0.0.0'
            self.SQL_ECHO = False
            self.PORT = os.environ.get('PORT', 5000)
            self.DATABASE_URL = os.environ.get('sqlalchemy.url', 'sqlite:///./test.db')
            self.LOG_FOLDER = os.environ.get('log-folder', './logs')
        elif mode == 'develop':
            self.DB_SERVER = '0.0.0.0'
            self.SQL_ECHO = False
            self.DEBUG = True
            self.PORT = os.environ.get('PORT', 5000)
            self.DATABASE_URL = 'sqlite:///./test.db'
        elif mode == 'test':
            self.DB_SERVER = 'localhost'
            self.SQL_ECHO = False
            self.DEBUG = True
            self.DATABASE_URL = 'sqlite:///./test.db'


if 'MODE' in os.environ:
    env = os.environ['MODE']
else:
    env = 'develop'

cli_config: Config = Config(env)
