import logging
import os
import pathlib
import sys
from logging.handlers import TimedRotatingFileHandler


# ----------------------------------------------------------------------

def set_gunicorn_custom_logger(path='./logs', is_absolute_path=False,
                              log_format="%(asctime)s - %(levelname)s - %(message)s"):
    """Init logging
    Arguments:
        path {string} -- absolute path to log directory
    Returns:
        logger -- logger class. Use as logger.info('message')
    """
    pathname = os.path.dirname(sys.argv[0])
    basedir = os.path.abspath(pathname)
    # print('full path =', os.path.abspath(pathname))
    # make log folder if not exist:
    log_path = path
    if is_absolute_path is False:
        log_path = os.path.abspath(os.path.join(
            basedir, path))
    # print('log_path', log_path)
    pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)
    # print(log_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    error_logger = logging.getLogger("gunicorn.error")
    access_logger = logging.getLogger("gunicorn.access")
    # error_logger = logging.getLogger("rotation log")
    # access_logger = logging.getLogger("rotation log access")
    formatter = logging.Formatter(log_format)

    access_handler = TimedRotatingFileHandler(log_path + '/access.log', when="d", interval=1, backupCount=5)
    access_handler.setFormatter(formatter)

    error_handler = TimedRotatingFileHandler(log_path + '/error.log', when="d", interval=1, backupCount=5)
    error_handler.setFormatter(formatter)

    error_logger.addHandler(error_handler)
    access_logger.addHandler(access_handler)
    return access_logger, error_logger


def create_timed_rotating_log(path='./logs', is_absolute_path=False, logger_name="Rotating Log", file_log='app.log',
                              log_format="%(asctime)s - %(levelname)s - %(message)s"):
    """Init logging
    Arguments:
        path {string} -- absolute path to log directory
    Returns:
        logger -- logger class. Use as logger.info('message')
    """
    pathname = os.path.dirname(sys.argv[0])
    basedir = os.path.abspath(pathname)
    # print('full path =', os.path.abspath(pathname))
    # make log folder if not exist:
    log_path = path
    if is_absolute_path is False:
        log_path = os.path.abspath(os.path.join(
            basedir, path))
    # print('log_path', log_path)
    pathlib.Path(log_path).mkdir(parents=True, exist_ok=True)
    # print(log_path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_path = log_path + '/' + file_log
    logger = logging.getLogger(logger_name)
    logger.setLevel(logger.level)
    formatter = logging.Formatter(log_format)

    handler = TimedRotatingFileHandler(log_path, when="S", interval=100)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
