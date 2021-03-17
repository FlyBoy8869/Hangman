import sys

from PyQt5.QtWidgets import QApplication

import hangman.patchexceptionhook as patch
from hangman.mainwindow import MainWindow

import hangman.loggingsetup as loggingsetup


def main():
    patch.patch_exception_hook()
    loggingsetup.setup_logging()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
