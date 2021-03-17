import argparse


def _do_nothing_ic(*a):
    """ Do nothing version of icecream.ic """
    return None if not a else (a[0] if len(a) == 1 else a)


def _parse_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--noconfirmexit",
        action="store_true",
        help="Don't confirm program exit.",
        required=False
    )

    parser.add_argument(
        "--debug_level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Level of debugging message to display.",
        required=False
    )

    parser.add_argument(
        "--length",
        type=int,
        default=-1,
        help="Select only words of the specified length"
    )

    parser.add_argument(
        "--debug",
        default=False,
        action="store_true"
    )

    parser.add_argument(
        "--body",
        choices=["plain", "chicken"],
        default="plain"
    )

    return parser.parse_args()


config = _parse_command_line()

try:
    from icecream import install, ic
except ImportError:
    def install(): pass
    ic = _do_nothing_ic
else:
    if config.debug:
        install()
        ic.configureOutput(includeContext=True)
    else:
        # even with a successful import of the icecream module
        # make sure the "do nothing" version of ic gets installed
        # if the --debug flag is not specified
        ic = _do_nothing_ic
        builtins = __import__("builtins")
        setattr(builtins, 'ic', ic)
