import sys

from PyQt5.QtWidgets import QApplication

import hangman.patchexceptionhook as patch
from hangman.mainwindow import MainWindow

import hangman.loggingsetup as loggingsetup


def main(args: dict):
    patch.patch_exception_hook()
    loggingsetup.setup_logging(args)
    app = QApplication(sys.argv)
    window = MainWindow(args)
    window.show()
    sys.exit(app.exec())
