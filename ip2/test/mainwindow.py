# This Python file uses the following encoding: utf-8
import os, sys
from pathlib import Path

from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile, QObject
from PySide2.QtUiTools import QUiLoader
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QDialog, QPushButton



def load_transaction_button_clicked():
    print("pb1 clicked")

def draw_grid_button_clicked():
    print("draw grid clicked")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.load_ui()
#        self.window.setWindowTitle("Minimal closed transation sets")
        self.loadTButton = QPushButton(self.findChild(QPushButton, "loadTButton"))
        self.drawGButton = QPushButton(self.findChild(QPushButton, "drawGButton"))


    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

#    def show(self):
 #       self.window.show()



if __name__ == "__main__":
    app = QApplication([])
    widget = MainWindow()

#    window.loadTButton.clicked.connect(load_transaction_button_clicked)
 #   window.drawGButton.clicked.connect(draw_grid_button_clicked)

    widget.show()
    sys.exit(app.exec_())
