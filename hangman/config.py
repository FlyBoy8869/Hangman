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
        help="Detail of debugging information to display.",
        required=False
    )

    parser.add_argument(
        "--range",
        type=int,
        nargs="+",
        choices={
            3, 4, 5, 6, 7, 8, 9, 10,
            11, 12, 13, 14, 15, 16, 17, 18,
            19, 20, 21, 22, 23, 24, 25,
            27, 28, 29, 31
        },
        default=0,
        help="Select only words of the specified lengths."
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
setattr(config, "word_file_path", "resources/words.dat")
setattr(config, "number_of_words", 370103)

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


def add_attribute(attr, value):
    global config
    setattr(config, attr, value)
