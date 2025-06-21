import sys
import os

def get_db_path():
    if getattr(sys, 'frozen', False):
        # Если программа собрана в exe, используем временную папку для ресурсов
        base_path = sys._MEIPASS
    else:
        # Обычный запуск: используем структуру проекта
        base_path = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_path, 'databases', 'DroneFireModel.db')
