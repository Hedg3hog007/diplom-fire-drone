# main.py
import sys
from PyQt5.QtWidgets import QApplication
from gui import GUI
from Fire_power_model import FireModel
import EA_model

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)

        # Создание модели
        self.model = FireModel()

        # Создание GUI и передача модели
        self.gui = GUI()
        self.gui.model = self.model  # Передаем модель в GUI

        # Начальные данные
        self.gui.update_graph()

    def run(self):
        self.gui.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = MainApp()
    app.run()