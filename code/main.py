# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui import GUI
from Fire_power_model import FireModel

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.gui = GUI()
        self.gui.update_graph()

    def run(self):
        self.gui.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = MainApp()
    app.run()