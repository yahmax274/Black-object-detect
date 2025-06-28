# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget
from view.main_windows import Ui_Form
from utils.controller import MainController

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.controller = MainController(self.ui)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
