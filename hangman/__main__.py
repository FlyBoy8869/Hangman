import sys

from PyQt5.QtWidgets import QApplication

import hangman.patchexceptionhook as patch
from hangman.mainwindow import MainWindow


def main(args: dict):
    patch.patch_exception_hook()
    app = QApplication(sys.argv)
    window = MainWindow(args)
    window.show()
    sys.exit(app.exec())
