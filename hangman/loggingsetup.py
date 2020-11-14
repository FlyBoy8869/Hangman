import logging

FORMAT = '%(levelname)s:%(asctime)-15s %(module)s.%(classname)s.%(funcName)s:line no. %(lineno)d, %(message)s'

_levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


def setup_logging(args: dict):
    if args["debug_level"]:
        logging.basicConfig(format=FORMAT, level=_levels[args["debug_level"]])
