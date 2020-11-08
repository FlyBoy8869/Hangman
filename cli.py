import argparse

from hangman.__main__ import main


def parse_args():
    description = "Hangman: Guess the letters of a word until successfully guessed or you are hung :P"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--noconfirmexit",
        action="store_true",
        help="Don't confirm program exit.",
        required=False
    )
    return vars(parser.parse_args())


if __name__ == '__main__':
    args = parse_args()
    main(args)
