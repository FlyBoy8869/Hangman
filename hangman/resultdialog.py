from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QDialog

from .designerforms import Ui_ResultDialog


class ResultDialog(QDialog, Ui_ResultDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Game Over")

    def run(self, image: QPixmap) -> int:
        self.label_result.setPixmap(image)
        return super().exec()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        self.accept()

    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.accept()
