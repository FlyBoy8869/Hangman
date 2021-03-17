import logging

from hangman.config import config

FORMAT = '%(levelname)s:%(asctime)-15s %(module)s.%(classname)s.%(funcName)s:line no. %(lineno)d, %(message)s'

_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


def setup_logging():
    if config.debug_level:
        logging.basicConfig(format=FORMAT, level=_levels[config.debug_level])
