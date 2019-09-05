import json


def read_config(file_name: str = "config.json") -> dict:
    with open(file_name, 'r') as json_file:
        cfg = json.load(json_file)
    return cfg


json_config: dict = read_config('./config.json')
development_key = 'dev'
production_key = 'prod'
private_key_file = './private.pem'
public_key_file = './public.pem'


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
    LOG_FOLDER = '/home/minhtuan/Documents/python-world/python-clean-architecture/logs'
    PRIVATE_KEY = open(private_key_file).read()
    PUBLIC_KEY = open(public_key_file).read()

    # mail settings
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    # gmail authentication
    MAIL_USERNAME = json_config.get('APP_MAIL_USERNAME', '')
    MAIL_PASSWORD = json_config.get('APP_MAIL_PASSWORD', '')

    # mail accounts
    MAIL_DEFAULT_SENDER = 'from@example.com'


class ProductionConfig(Config):
    """Uses production database server."""
    DB_SERVER = '0.0.0.0'
    PORT = json_config.get('PORT', 5000)
    DATABASE_URL = json_config.get('sqlalchemy.url', 'sqlite:///./test.db')
    LOG_FOLDER = json_config.get('log-folder', '/home/minhtuan/Documents/python-world/python-clean-architecture/logs')


class DevelopmentConfig(Config):
    DB_SERVER = '0.0.0.0'
    DEBUG = True
    PORT = json_config.get('PORT', 5000)
    DATABASE_URL = json_config.get('sqlalchemy.url', 'sqlite:///./test.db')


class TestingConfig(Config):
    DB_SERVER = 'localhost'
    DEBUG = True
    DATABASE_URL = 'sqlite:///:memory:'


config = {
    'default': Config,
    'develop': DevelopmentConfig,
    'production': ProductionConfig,
    'test': TestingConfig
}

cli_config = config['production']
