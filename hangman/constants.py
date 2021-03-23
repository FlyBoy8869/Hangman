from enum import Enum

# rgba
orange_shade = (240, 139, 69, 255)
pink_shade = (215, 26, 90, 255)

alphabet = frozenset("abcdefghijklmnopqrstuvwxyz")

image_logo_path = "resources/images/Logo_1.png"
spinner = "resources/images/spinners/spinner.gif"


class GameResult(Enum):
    WON = 1
    LOST = 2
