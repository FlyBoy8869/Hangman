import sys

from PyQt6.QtWidgets import QApplication

from hangman.mainwindow import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
