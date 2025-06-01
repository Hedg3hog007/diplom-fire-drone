# gui.py
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem, QPushButton, QInputDialog, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from DroneFireModel import DataBase_data
from Fire_power_model import FireModel
from Fire_hose_model import Fire_hose
from UAV_model import UAV
from EA_model import EA
import random
import numpy as np



class DebugTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.Re_figure = Figure(figsize=(5, 4), dpi=100)
        self.coef_figure = Figure(figsize=(5, 4), dpi=100)
        self.fric_figure = Figure(figsize=(5, 4), dpi=100)
        self.cons_figure = Figure(figsize=(5, 4), dpi=100)

        self.Re_canvas = FigureCanvas(self.Re_figure)
        self.coef_canvas = FigureCanvas(self.coef_figure)
        self.fric_canvas = FigureCanvas(self.fric_figure)
        self.cons_canvas = FigureCanvas(self.cons_figure)

        layout.addWidget(self.Re_canvas)
        layout.addWidget(self.coef_canvas)
        layout.addWidget(self.fric_canvas)
        layout.addWidget(self.cons_canvas)

        Re_ax = self.Re_figure.add_subplot(111)
        coef_ax = self.coef_figure.add_subplot(111)
        fric_ax = self.fric_figure.add_subplot(111)
        cons_ax = self.cons_figure.add_subplot(111)

        ea = EA(1, 1)
        Re = 1
        Re_arr = np.array([])
        coef_arr = np.array([])
        fric_arr = np.array([])
        cons_arr = np.array([])

        # while Re > 0:
        #     Re, coef, fric, cons  = ea.EAConsumption_Reynolds()
        #     Re_arr = np.append(Re_arr, Re)
        #     coef_arr = np.append(coef_arr, coef)
        #     fric_arr = np.append(fric_arr, fric)
        #     cons_arr = np.append(cons_arr, cons)

        x = np.linspace(0, len(Re_arr), len(Re_arr))

        Re_ax.plot(x, Re_arr, label="Число Рейнольдса")
        coef_ax.plot(x, coef_arr, label="Коэффициент трения")
        fric_ax.plot(x, fric_arr, label="Потери на трение")
        cons_ax.plot(x, cons_arr, label="Расход воды")

        Re_ax.set_title("Рейнольдс")
        coef_ax.set_title("Коэффициент трения")
        fric_ax.set_title("Потери на трение")
        cons_ax.set_title("Расход воды")

        Re_ax.legend()
        coef_ax.legend()
        fric_ax.legend()
        cons_ax.legend()

        self.Re_canvas.draw()
        self.coef_canvas.draw()
        self.fric_canvas.draw()
        self.cons_canvas.draw()

class DatabaseTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.db = DataBase_data()
        
        # Список таблиц
        list_label = QLabel("Выберите таблицу:")
        self.table_combobox = QComboBox()
        self.table_combobox.addItems(self.db._models.keys())
        self.table_combobox.currentTextChanged.connect(self.table_changed)

        table_layout = QVBoxLayout()
        table_layout.addWidget(list_label)
        table_layout.addWidget(self.table_combobox)
        layout.addLayout(table_layout)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.edit_btn = QPushButton("Редактировать")
        self.delete_btn = QPushButton("Удалить")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.delete_btn.clicked.connect(self.delete_record)

        # Таблица для отображения данных
        self.data_table = QTableWidget()
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.data_table)

        # Показать первую таблицу по умолчанию
        self.table_changed(self.table_combobox.currentText())

    def table_changed(self, selected_table):
        tablename = self.db._models.get(selected_table)
        records = self.db.session.query(tablename).all()
        if not records:
            self.data_table.clear()
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            return

        columns = [col for col in records[0].__table__.columns.keys()]
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)
        self.data_table.setRowCount(len(records))

        for row_idx, record in enumerate(records):
            for col_idx, col_name in enumerate(columns):
                value = getattr(record, col_name)
                self.data_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.data_table.resizeColumnsToContents()

    def add_record(self):
        selected_table = self.table_combobox.currentText()
        model_class = self.db._models.get(selected_table)
        columns = [col.name for col in model_class.__table__.columns if col.name != "id"]
        values = {}
        for col in columns:
            val, ok = QInputDialog.getText(self, "Добавить запись", f"{col}:")
            if not ok:
                return
            values[col] = val
        try:
            self.db.add_record(selected_table, **values)
            self.table_changed(selected_table)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка добавления: {e}")

    def edit_record(self):
        selected_table = self.table_combobox.currentText()
        row = self.data_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Редактирование", "Выберите запись для редактирования.")
            return
        model_class = self.db._models.get(selected_table)
        columns = [col.name for col in model_class.__table__.columns if col.name != "id"]
        id_item = self.data_table.item(row, 0)
        if not id_item:
            return
        record_id = int(id_item.text())
        values = {}
        for col_idx, col in enumerate(columns, start=1):
            old_val = self.data_table.item(row, col_idx).text()
            val, ok = QInputDialog.getText(self, "Редактировать запись", f"{col}:", text=old_val)
            if not ok:
                return
            values[col] = val
        try:
            self.db.update_record(selected_table, record_id, **values)
            self.table_changed(selected_table)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка редактирования: {e}")

    def delete_record(self):
        selected_table = self.table_combobox.currentText()
        row = self.data_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Удаление", "Выберите запись для удаления.")
            return
        id_item = self.data_table.item(row, 0)
        if not id_item:
            return
        record_id = int(id_item.text())
        reply = QMessageBox.question(self, "Удаление", "Удалить выбранную запись?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db.delete_record(selected_table, record_id)
                self.table_changed(selected_table)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Динамическая модель тушения пожаров")
        self.setGeometry(100, 100, 1800, 900)

        # Создание QTabWidget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Главная вкладка (ваш основной интерфейс)
        self.main_widget = QWidget()
        self.tabs.addTab(self.main_widget, "Главное окно")

        # Вкладка для отладки
        self.debug_tab = DebugTab(self)
        self.tabs.addTab(self.debug_tab, "Отладка")
        self.layout = QHBoxLayout(self.main_widget)

        # Вкладка для базы данных
        self.database_tab = DatabaseTab(self)
        self.tabs.addTab(self.database_tab, "База данных")

        # График интенсивности пожара
        self.left_layout = QVBoxLayout()
        self.figure_fire = Figure(figsize=(6, 4), dpi=100)
        self.canvas_fire = FigureCanvas(self.figure_fire)
        self.ax_fire = self.figure_fire.add_subplot(111)
        self.line, = self.ax_fire.plot([], [], label="Мощность тепловыделения, Дж")
        self.ax_fire.legend(loc = 'upper right')
        self.ax_fire.set_title("Развитие пожара")
        self.ax_fire.set_xlabel("Время (с)")
        self.ax_fire.set_ylabel("Интенсивность пожара (Дж)")
        self.left_layout.addWidget(self.canvas_fire)
        self.layout.addLayout(self.left_layout)

        # График интенсивности тушения
        self.right_layout = QVBoxLayout()
        self.layout.addLayout(self.right_layout)
        self.figure_hose = Figure(figsize=(6, 4), dpi=100)
        self.canvas_hose = FigureCanvas(self.figure_hose)
        self.ax_hose = self.figure_hose.add_subplot(111)
        self.right_layout.addWidget(self.canvas_hose)

        # Гистограмма времени тушения от конфигурации БАС
        self.figure_time_by_UAS = Figure(figsize=(8, 4), dpi=100)
        self.canvas_time_by_UAS = FigureCanvas(self.figure_time_by_UAS)
        self.ax_time_by_UAS = self.figure_time_by_UAS.add_subplot(111)
        self.layout.addWidget(self.canvas_time_by_UAS)

        #График времени тушения от расхода бортовой БАС
        self.figure_time_by_consumption = Figure(figsize=(6, 4), dpi=100)
        self.canvas_time_by_consumption = FigureCanvas(self.figure_time_by_consumption)
        self.ax_time_by_consumption = self.figure_time_by_consumption.add_subplot(111)
        self.ax_time_by_consumption.set_title("Время тушения от расхода для бортовой БАС")
        self.ax_time_by_consumption.set_ylabel("Время тушения (с)")
        self.ax_time_by_consumption.set_xlabel("Расход воды (л/с)")
        self.right_layout.addWidget(self.canvas_time_by_consumption)

        # Инициализация начальных параметров
        self.area = 60  # Начальная площадь помещения
        self.height = 40 # Начальная высота тушения
        self.EA_consumption_tank = 11 # Расход воды бортовой БАС (л/с)
        self.time_extinguishing_start = random.randint(8, 13)  # Начальное время тушения
        self.db = DataBase_data()
        self.hose_names = [] # Список названий пожарных рукавов
        self.hose_tablename = self.db._models.get('Пожарные рукава')
        for i in range (len(self.db.session.query(self.hose_tablename).all())):
            self.hose_names.append(self.db.record_get('Пожарные рукава', i + 1, 'name'))

        self.selected_hose_UAV_hose = self.hose_names[0] # Начальный тип рукава
        self.hose_UAV_hose_id = 1 
        self.selected_tank_UAV_hose = self.hose_names[0]
        self.tank_UAV_hose_id = 1
 
        # Список типов помещений из базы данных
        self.buildings_tablename = self.db._models.get('Помещения')
        self.buildings_names = self.db.session.query(self.buildings_tablename.name).all()

        self.selected_building = self.buildings_names[0] # Начальный тип помещения
        self.building_id = 1 

        # Список дронов из базы данных
        self.UAV_tablename = self.db._models.get('Дроны')
        self.UAV_names = self.db.session.query(self.UAV_tablename.name).all()

        self.selected_tank_UAV = self.UAV_names[0] # Начальный тип дрона
        self.tank_UAV_id = 1
        self.selected_hose_UAV = self.UAV_names[0] 
        self.hose_UAV_id = 1

        # Создание полей ввода
        self.create_input_layout()
        self.create_sliders()
        self.create_height_input()
        self.create_buildings_combobox()
        self.create_UAV_var_layout()
        self.create_hose_UAV_hose_combobox()
        self.create_tank_UAV_hose_combobox()
        self.create_tank_UAV_combobox()
        self.create_hose_UAV_combobox()
        self.chart_time_by_consumption() #График зависимости времени тушения от расхода для бортового ОТВ

    def create_input_layout(self):
        self.parameters_layout = QVBoxLayout()
        self.left_layout.addLayout(self.parameters_layout)

    def create_sliders(self):
        """Создает слайдеры для управления параметрами."""
        def create_slider(label_text, min_val, max_val, default_val, callback, object_name):
            slider_layout = QVBoxLayout()

            label = QLabel(f"{label_text} {default_val}")
            slider_layout.addWidget(label)

            slider = QSlider(orientation=1)  # Горизонтальный слайдер
            slider.setObjectName(object_name)
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(default_val)
            slider.valueChanged.connect(lambda value: self.update_label(label, value))
            slider.valueChanged.connect(callback)
            slider_layout.addWidget(slider)

            self.parameters_layout.addLayout(slider_layout)
            return slider

        area_slider = create_slider(
            label_text="Площадь помещения (м2):",
            min_val=1,
            max_val=100,
            default_val=self.area,
            callback = self.area_changed,
            object_name="area_slider"
        )

        time_extinguishing_start_slider = create_slider(
            label_text="Время начала тушения (мин):",
            min_val = 5,
            max_val = 30,
            default_val = self.time_extinguishing_start,
            callback = self.time_extinguishing_start_changed,
            object_name = "time_extinguishing_start_slider"
        )
        
    def create_buildings_combobox(self):
        combo_layout = QVBoxLayout()
                          
        # Метка для списка
        label = QLabel("Тип помещения:")
        combo_layout.addWidget(label)

        # Создание QComboBox
        self.buildings_combobox = QComboBox()
        self.buildings_combobox.addItems([(result.name) for result in self.buildings_names])
        self.buildings_combobox.currentTextChanged.connect(self.buildings_combobox_changed)  # Обработчик события
        combo_layout.addWidget(self.buildings_combobox)

        # Добавление в макет
        self.parameters_layout.addLayout(combo_layout)
    
    def create_height_input(self):

        height_layout = QVBoxLayout()

        # Метка для поля ввода
        label = QLabel(f"Высота тушения (м): {self.height}")
        height_layout.addWidget(label)
        self.height_input = QLineEdit(str(self.height))
        self.height_input.setPlaceholderText("Введите высоту (м)")  # Подсказка
        self.height_input.textChanged.connect(lambda text: self.height_changed(text, label)) # Обработчик события
        height_layout.addWidget(self.height_input)

        # Добавление в макет
        self.parameters_layout.addLayout(height_layout)

    def create_UAV_var_layout(self):

        self.refresh_btn = QPushButton("Обновить данные БД")
        self.redraw_btn = QPushButton("Пересчитать")

        self.redraw_btn.clicked.connect(self.update_graph)
        self.refresh_btn.clicked.connect(self.refresh_main_tab)

        self.UAV_layout = QVBoxLayout()
        self.UAV_layout.addWidget(self.refresh_btn)
        self.UAV_layout.addWidget(self.redraw_btn)
    
        self.UAV_var_layout = QHBoxLayout()
        self.UAV_layout.addLayout(self.UAV_var_layout)

        self.parameters_layout.addLayout(self.UAV_layout)

        self.hose_UAV_main_layout = QVBoxLayout()
        self.tank_UAV_main_layout = QVBoxLayout()

        self.UAV_var_layout.addLayout(self.hose_UAV_main_layout)
        self.UAV_var_layout.addLayout(self.tank_UAV_main_layout)

        self.hose_UAV_main_layout.addWidget(QLabel('Прицепной пожарный рукав'))
        self.tank_UAV_main_layout.addWidget(QLabel('Бортовой резервуар'))

    def create_hose_UAV_hose_combobox(self):
        
        uav_combo_layout = QVBoxLayout()

        label = QLabel("Тип рукава:")
        uav_combo_layout.addWidget(label)

        # Создание QComboBox
        self.hose_UAV_hose_combobox = QComboBox()
        self.hose_UAV_hose_combobox.addItems(self.hose_names)
        self.hose_UAV_hose_combobox.currentTextChanged.connect(self.hose_UAV_hose_combobox_changed)
        uav_combo_layout.addWidget(self.hose_UAV_hose_combobox)

        # Добавление в макет
        self.hose_UAV_main_layout.addLayout(uav_combo_layout)

    def create_tank_UAV_hose_combobox(self):
        tank_uav_combo_layout = QVBoxLayout()
                          
        label = QLabel(f"Расход воды бортового ОТВ (л/с): {self.EA_consumption_tank}")
        tank_uav_combo_layout.addWidget(label)

        self.consumption_slider = QSlider(orientation=1)
        self.consumption_slider.setObjectName("consumption_slider")
        self.consumption_slider.setMinimum(1)
        self.consumption_slider.setMaximum(20)
        self.consumption_slider.setValue(self.EA_consumption_tank)
        self.consumption_slider.valueChanged.connect(lambda value: self.update_label(label, value))
        tank_uav_combo_layout.addWidget(self.consumption_slider)

        self.tank_UAV_main_layout.addLayout(tank_uav_combo_layout)
    
    def create_tank_UAV_combobox(self):
        tank_UAV_combo_layout = QVBoxLayout()
                          
        # Метка для списка
        label = QLabel("Выберите дрон:")
        tank_UAV_combo_layout.addWidget(label)

        # Выпадающий список дронов
        self.tank_UAV_combobox = QComboBox()
        self.tank_UAV_combobox.addItems([(result.name) for result in self.UAV_names])
        self.tank_UAV_combobox.currentTextChanged.connect(self.tank_UAV_combobox_changed)
        tank_UAV_combo_layout.addWidget(self.tank_UAV_combobox)

        # Поля для отображения характеристик
        self.tank_UAV_mass_label = QLabel()
        self.tank_UAV_payload_label = QLabel()
        self.tank_UAV_flight_time_label = QLabel()
        record = self.db.session.query(self.UAV_tablename).filter_by(id = self.tank_UAV_id).first()
        self.tank_UAV_mass_label.setText(f"Масса дрона: {record.mass} кг")
        self.tank_UAV_payload_label.setText(f"Полезная нагрузка: {record.payload} кг")
        self.tank_UAV_flight_time_label.setText(f"Время полёта: {record.flight_time} мин")

        tank_UAV_combo_layout.addWidget(self.tank_UAV_mass_label)
        tank_UAV_combo_layout.addWidget(self.tank_UAV_payload_label)
        tank_UAV_combo_layout.addWidget(self.tank_UAV_flight_time_label)

        self.tank_UAV_main_layout.addLayout(tank_UAV_combo_layout)

        self.tank_UAV_fire_extinguishing_time_label = QLabel()
        self.tank_UAV_efficiency_label = QLabel()

        self.tank_UAV_main_layout.addWidget(self.tank_UAV_fire_extinguishing_time_label)
        self.tank_UAV_main_layout.addWidget(self.tank_UAV_efficiency_label)

    def create_hose_UAV_combobox(self):
        hose_UAV_combo_layout = QVBoxLayout()
                          
        # Метка для списка
        label = QLabel("Выберите дрон:")
        hose_UAV_combo_layout.addWidget(label)

        # Выпадающий список дронов
        self.hose_UAV_combobox = QComboBox()
        self.hose_UAV_combobox.addItems([(result.name) for result in self.UAV_names])
        self.hose_UAV_combobox.currentTextChanged.connect(self.hose_UAV_combobox_changed)
        hose_UAV_combo_layout.addWidget(self.hose_UAV_combobox)

        # Поля для отображения характеристик
        self.hose_UAV_mass_label = QLabel()
        self.hose_UAV_payload_label = QLabel()
        self.hose_UAV_flight_time_label = QLabel()
        record = self.db.session.query(self.UAV_tablename).filter_by(id = self.hose_UAV_id).first()
        self.hose_UAV_mass_label.setText(f"Масса дрона: {record.mass} кг")
        self.hose_UAV_payload_label.setText(f"Полезная нагрузка: {record.payload} кг")
        self.hose_UAV_flight_time_label.setText(f"Время полёта: {record.flight_time} мин")

        hose_UAV_combo_layout.addWidget(self.hose_UAV_mass_label)
        hose_UAV_combo_layout.addWidget(self.hose_UAV_payload_label)
        hose_UAV_combo_layout.addWidget(self.hose_UAV_flight_time_label)

        self.hose_UAV_main_layout.addLayout(hose_UAV_combo_layout)

        self.hose_UAV_fire_extinguishing_time_label = QLabel()
        self.hose_UAV_efficiency_label = QLabel()

        self.hose_UAV_main_layout.addWidget(self.hose_UAV_fire_extinguishing_time_label)
        self.hose_UAV_main_layout.addWidget(self.hose_UAV_efficiency_label)

    def buildings_combobox_changed(self, text):
        self.selected_building = text
        # Обновление ID выбранного здания по имени
        record = self.db.session.query(self.buildings_tablename).filter_by(name = self.selected_building).first()
        self.building_id = getattr(record, 'id')

    def hose_UAV_combobox_changed(self, text):
        self.selected_hose_UAV_hose = text
        record = self.db.session.query(self.UAV_tablename).filter_by(name = self.selected_hose_UAV_hose).first()
        self.hose_UAV_id = getattr(record, 'id')
        self.hose_UAV_mass_label.setText(f"Масса дрона: {record.mass} кг")
        self.hose_UAV_payload_label.setText(f"Полезная нагрузка: {record.payload} кг")
        self.hose_UAV_flight_time_label.setText(f"Время полёта: {record.flight_time} мин")

    def tank_UAV_combobox_changed(self, text):
        self.selected_tank_UAV_hose = text
        # Обновление ID выбранного дрона по имени
        record = self.db.session.query(self.UAV_tablename).filter_by(name = self.selected_tank_UAV_hose).first()
        self.tank_UAV_id = getattr(record, 'id')
        self.EA_consumption_tank = round(getattr(record, 'payload') / 20)
        self.consumption_slider.setValue(self.EA_consumption_tank)
        self.tank_UAV_mass_label.setText(f"Масса дрона: {record.mass} кг")
        self.tank_UAV_payload_label.setText(f"Полезная нагрузка: {record.payload} кг")
        self.tank_UAV_flight_time_label.setText(f"Время полёта: {record.flight_time} мин")

    def hose_UAV_hose_combobox_changed(self, text):
        self.selected_hose_UAV_hose = text
        record = self.db.session.query(self.hose_tablename).filter_by(name = self.selected_hose_UAV_hose).first()
        self.hose_UAV_hose_id = getattr(record, 'id')

    def area_changed(self, value):
        self.area = value

    def time_extinguishing_start_changed(self, value):
        self.time_extinguishing_start = value

    def consumption_tank_slider_changed(self, value):
        self.EA_consumption_tank = value

    def height_changed(self, text, label):
        
        if text == "":
            self.height = 0
        else:
            if int(text) < 0:
                self.height = 0
            else:
                self.height = int(text)
        label.setText(f"Высота тушения (м): {self.height}")
   
    def update_label(self, label, value):
        label.setText(f"{label.text().split('(')[0].strip()} ({value})")

    def update_graph(self):
        # Обновление графика развития пожара
        area_slider = self.findChild(QSlider, "area_slider")
        self.area = area_slider.value()
        self.ax_fire.clear()
        x, y = self.natural_fire_spread()
        self.ax_fire.plot(x, y,  label = "Натуральное развитие пожара")

        # Обновление графика времени тушения от расхода бортовой БАС
        self.chart_time_by_consumption()
        self.ax_time_by_consumption.legend(loc = 'lower left')
        self.ax_time_by_consumption.relim()
        self.ax_time_by_consumption.autoscale_view()
        self.canvas_time_by_consumption.draw()
        
        #Обновление гистограммы времени тушения
        self.chart_time_by_UAS()
        self.ax_time_by_UAS.relim()
        self.ax_time_by_UAS.autoscale_view()
        self.canvas_time_by_UAS.draw()

        # Обновление графика противодействия пожару
        x_ext, y_ext = self.hose_UAV_fire_extinguishing_simulation()
        x_ext_tank_uav, y_ext_tank_uav = self.tank_UAV_fire_extinguishing_simulation()
        self.ax_fire.set_title("Развитие пожара")
        self.ax_fire.set_xlabel("Время (с)")
        self.ax_fire.set_ylabel("Интенсивность пожара (Дж/с)")
        self.ax_fire.plot(x_ext, y_ext, label="прицепной рукав")
        self.ax_fire.plot(x_ext_tank_uav, y_ext_tank_uav, label="бортовой резервуар")

        self.ax_fire.legend(loc = 'upper right')
        self.ax_fire.relim()
        self.ax_fire.autoscale_view()
        self.canvas_fire.draw()

        # Обновление графика интенсивности тушения
        heights = np.linspace(0, self.height, self.height)
                
        self.ax_hose.clear()
        self.ax_hose.set_title("Интенсивность тушения от высоты для прицепного рукава")
        self.ax_hose.set_xlabel("Высота тушения (м)")
        self.ax_hose.set_ylabel("Интенсивность тушения (Дж/с)")

        for i in range (len(self.hose_names)):
            intensities = self.calculate_hose_intensities(heights, hose_id = i + 1)
            self.ax_hose.plot(heights, intensities, label = self.hose_names[i])

        max_fire_plot = np.linspace(self.max_fire_power, self.max_fire_power, len(heights))
        self.ax_hose.plot(heights, max_fire_plot, label = "Макс. мощность пожара", linestyle='--', color='red')

        self.ax_hose.legend(loc = 'upper left')
        self.ax_hose.relim()
        self.ax_hose.autoscale_view()
        self.canvas_hose.draw()
        
    def calculate_hose_intensities(self, heights, hose_id):
        ea_model = EA(1, hose_id)
        intensities = []
        for h in heights:
            intensities.append(ea_model.HeatAbsorption())

        return intensities 

    def natural_fire_spread(self):
        # Рассчитываем мощность пожара без учета тушения
        self.fire_model = FireModel(self.building_id, self.area)
        self.max_fire_power = self.fire_model.fire_max_power()

        y = np.array([])
        fire_power = 0
        time = 0
        while fire_power >= 0:
            y = np.append(y, self.fire_model.fire_calculate(time))
            fire_power = y[-1]
            time += 1
        
        x = np.linspace(0, time, time)
           
        return x, y
  
    def hose_UAV_fire_extinguishing_simulation(self):
        # Инициализация параметров для моделирования
        y = np.array([])
        time = 0
        fire_power = 0
        weight = 0
        ea_model = EA(1, self.hose_UAV_hose_id)
        hose_uav_model = UAV(self.hose_UAV_id)
        hose_model = Fire_hose(self.hose_UAV_hose_id)
        
        for i in range (self.height):
            weight += ea_model.weight_per_meter()
        if weight > hose_uav_model.payload:
            self.hose_UAV_fire_extinguishing_time_label.setText("Дрон не может поднять рукав")
            self.hose_UAV_fire_extinguishing_time_label.setStyleSheet('background-color: lightcoral')
            x = np.linspace(0, time, time)
            return x, y
        for i in range (self.height):
            EA_power = ea_model.HeatAbsorption()

        hose_UAV_fire_model = FireModel(self.building_id, self.area)
        

        # Моделирование тушения
        while (hose_UAV_fire_model.max_fire_area - hose_UAV_fire_model.extinguished_area > 0) and (fire_power >= 0):

            # Развитие пожара до начала тушения
            if time < self.time_extinguishing_start * 60:
                y = np.append(y, hose_UAV_fire_model.fire_calculate(time))
                fire_power = y[-1]
                time += 1

            # Тушение пожара
            else:
                y = np.append(y, hose_UAV_fire_model.fire_calculate(time))
                fire_power = y[-1]
                fire_power_per_meter = fire_power / (self.area - hose_UAV_fire_model.extinguished_area)
                if fire_power_per_meter < EA_power:
                    burning_temperature = 800
                    while burning_temperature > 350:
                        delta_temperature = (EA_power - fire_power_per_meter) / (hose_UAV_fire_model.heat_capacity * hose_UAV_fire_model.fire_load_specific_mass)
                        burning_temperature -= delta_temperature
                        time += 1
                        y = np.append(y, hose_UAV_fire_model.fire_calculate(time))
                    hose_UAV_fire_model.extinguished_area += 1
                else:
                    self.hose_UAV_fire_extinguishing_time_label.setStyleSheet("background-color: lightcoral")
                    self.hose_UAV_fire_extinguishing_time_label.setText("Пожар не потушен")
                    time += 1
                    x = np.linspace(0, time, time)
                    return x, y
                time += 1


        hose_UAV_fire_extinguishing_time = time - (self.time_extinguishing_start * 60)
        self.hose_UAV_fire_extinguishing_time_label.setText(f"Пожар потушен за {hose_UAV_fire_extinguishing_time // 60} мин {hose_UAV_fire_extinguishing_time % 60} сек")
        self.hose_UAV_fire_extinguishing_time_label.setStyleSheet('background-color: lightgreen')
        self.hose_UAV_efficiency_label.setText(f"Энерговооружённость: {round(EA_power / (hose_uav_model.mass + weight))} Дж/кг, масса системы: {round(hose_uav_model.mass + weight)} кг")

        x = np.linspace(0, time, time)
        return x, y

    def tank_UAV_fire_extinguishing_simulation(self):
        
        # Инициализация переменных
        tank_UAV_model = UAV(self.tank_UAV_id) 
        tank_UAV_fire_model = FireModel(self.building_id, self.area)
        EA_model = EA(1, 1)
        EA_consumption = self.EA_consumption_tank / 1000 # Расход в м3/с
        EA_power = EA_model.HeatAbsorption_tank(EA_consumption)
        time = 0
        fire_power = 0
        y = np.array([])
        current_flight_time = tank_UAV_model.lift_time(self.height) 

        time_start = (self.time_extinguishing_start * 60) + tank_UAV_model.service_time() + tank_UAV_model.lift_time(self.height) 
        for i in range (time_start):
            y = np.append(y, tank_UAV_fire_model.fire_calculate(time))
            time += 1

        UAV_EA_volume = tank_UAV_model.payload / EA_model.EA_density
        time_extinguishing = round(UAV_EA_volume / EA_consumption)
        if time_extinguishing == 0:
            time_extinguishing = 1

        while (tank_UAV_fire_model.max_fire_area - tank_UAV_fire_model.extinguished_area > 0) and (fire_power) >= 0:
            
            # Тушение пожара
            current_extenguishing_time = 0
            while (time_extinguishing - current_extenguishing_time) > 0:
                y = np.append(y, tank_UAV_fire_model.fire_calculate(time))
                fire_power = y[-1]
                
                # Если пожар потушен
                if (tank_UAV_fire_model.max_fire_area - tank_UAV_fire_model.extinguished_area <= 0) or (fire_power) < 0: 
                    tank_UAV_fire_extinguishing_time = time - (self.time_extinguishing_start * 60)
                    self.tank_UAV_fire_extinguishing_time_label.setStyleSheet("background-color: lightgreen")
                    self.tank_UAV_fire_extinguishing_time_label.setText(f"Пожар потушен за {tank_UAV_fire_extinguishing_time // 60} мин {tank_UAV_fire_extinguishing_time % 60} сек")
                    self.tank_UAV_efficiency_label.setText(f"Эффективность: {round(EA_power / (tank_UAV_model.mass + tank_UAV_model.payload))} Дж/кг, масса системы: {round(tank_UAV_model.mass + tank_UAV_model.payload)} кг")
                    time += 1
                    x = np.linspace(0, time, time)
                    return x, y
                # Если пожар не потушен
                fire_power_per_meter = fire_power / (self.area - tank_UAV_fire_model.extinguished_area)
                if EA_power > fire_power_per_meter:
                    burning_temperature = 800
                    while burning_temperature > 350 and (time_extinguishing - current_extenguishing_time) > 0:
                        delta_temperature = (EA_power - fire_power_per_meter) / (tank_UAV_fire_model.heat_capacity * (tank_UAV_fire_model.fire_load_specific_mass - tank_UAV_fire_model.burnout_speed * max(0, time - tank_UAV_fire_model.time_max_power)))
                        burning_temperature -= delta_temperature
                        time += 1
                        current_extenguishing_time += 1
                        current_flight_time += 1
                        y = np.append(y, tank_UAV_fire_model.fire_calculate(time))
                    tank_UAV_fire_model.extinguished_area += 1
                    time += 1
                    current_flight_time += 1
                
            
            # Вводим модель свободного горения
            natural_fire_model = FireModel(self.building_id, tank_UAV_fire_model.extinguished_area)
            time_free_burn = 0
            # Снижение дрона
            for i in range (tank_UAV_model.descend_time(self.height)):
                fire_power = tank_UAV_fire_model.fire_calculate(time)
                power_free_burn = natural_fire_model.fire_calculate(time_free_burn)
                time_free_burn += 1
                time += 1
                current_flight_time += 1
                y = np.append(y, fire_power + power_free_burn)
            
            # Заправка резервуара
            for i in range (tank_UAV_model.EA_refill_time()):
                fire_power = tank_UAV_fire_model.fire_calculate(time)
                power_free_burn = natural_fire_model.fire_calculate(time_free_burn)
                time_free_burn += 1
                time += 1
                y = np.append(y, fire_power + power_free_burn)

            if (tank_UAV_model.flight_time * 60) < (current_flight_time + tank_UAV_model.lift_time(self.height) + tank_UAV_model.descend_time(self.height) + time_extinguishing):
                for i in range (tank_UAV_model.service_time()):
                    fire_power = tank_UAV_fire_model.fire_calculate(time)
                    power_free_burn = natural_fire_model.fire_calculate(time_free_burn)
                    time_free_burn += 1
                    time += 1
                    y = np.append(y, fire_power + power_free_burn)
                current_flight_time = 0

            # Подъём дрона
            for i in range (tank_UAV_model.lift_time(self.height)):
                fire_power = tank_UAV_fire_model.fire_calculate(time)
                power_free_burn = natural_fire_model.fire_calculate(time_free_burn)
                time_free_burn += 1
                time += 1
                current_flight_time += 1
                y = np.append(y, fire_power + power_free_burn)
            tank_UAV_fire_model.extinguished_area -= natural_fire_model.fire_area

        if (tank_UAV_fire_model.max_fire_area - tank_UAV_fire_model.extinguished_area > 0) and (fire_power)  >= 0:
            self.tank_UAV_fire_extinguishing_time_label.setText("Пожар не потушен")
            self.tank_UAV_fire_extinguishing_time_label.setStyleSheet('background-color: lightcoral')
        else:
            tank_UAV_fire_extinguishing_time = time - (self.time_extinguishing_start * 60)
            self.tank_UAV_fire_extinguishing_time_label.setText(f"Пожар потушен за {tank_UAV_fire_extinguishing_time // 60} мин {tank_UAV_fire_extinguishing_time % 60} сек")
            self.tank_UAV_fire_extinguishing_time_label.setStyleSheet("background-color: lightgreen")
            self.tank_UAV_efficiency_label.setText(f"Энерговооружённость: {round(EA_power / (tank_UAV_model.mass + tank_UAV_model.payload))} Дж/кг, масса системы: {round(tank_UAV_model.mass + tank_UAV_model.payload)} кг")
         
        x = np.linspace(0, time, time)
        return x, y

    def refresh_main_tab(self):
        # Обновить рукава
        self.hose_UAV_hose_combobox.blockSignals(True)
        self.tank_UAV_hose_combobox.blockSignals(True)
        self.hose_UAV_hose_combobox.clear()
        self.tank_UAV_hose_combobox.clear()
        self.hose_names = [self.db.record_get('Пожарные рукава', i + 1, 'name')
                           for i in range(len(self.db.session.query(self.hose_tablename).all()))]
        self.hose_UAV_hose_combobox.addItems(self.hose_names)
        self.tank_UAV_hose_combobox.addItems(self.hose_names)
        self.hose_UAV_hose_combobox.blockSignals(False)
        self.tank_UAV_hose_combobox.blockSignals(False)

        # Обновить помещения
        self.buildings_combobox.blockSignals(True)
        self.buildings_combobox.clear()
        self.buildings_names = self.db.session.query(self.buildings_tablename.name).all()
        self.buildings_combobox.addItems([result.name for result in self.buildings_names])
        self.buildings_combobox.blockSignals(False)

        # Обновить дроны
        self.tank_UAV_combobox.blockSignals(True)
        self.hose_UAV_combobox.blockSignals(True)
        self.tank_UAV_combobox.clear()
        self.hose_UAV_combobox.clear()
        self.UAV_names = self.db.session.query(self.UAV_tablename.name).all()
        self.tank_UAV_combobox.addItems([result.name for result in self.UAV_names])
        self.hose_UAV_combobox.addItems([result.name for result in self.UAV_names])
        self.tank_UAV_combobox.blockSignals(False)
        self.hose_UAV_combobox.blockSignals(False)

        # Обновить графики

    def chart_time_by_consumption(self):
        self.ax_time_by_consumption.clear()
        for j in range (len(self.UAV_names)):
            self.tank_UAV_id = j + 1
            self.time_by_consumption = self.dependence_time_by_consumption()
            self.ax_time_by_consumption.plot(self.time_by_consumption[0], self.time_by_consumption[1], label=f"{self.UAV_names[j].name}")
        self.tank_UAV_id = 1

    def dependence_time_by_consumption(self):
        max_consumption = 20
        consumption_values = np.linspace(1, max_consumption, max_consumption)
        time = np.array([])

        for i in range(1,max_consumption + 1,1):
            self.EA_consumption_tank = i
            time = np.append(time, self.tank_UAV_fire_extinguishing_simulation()[0][-1] - self.time_extinguishing_start * 60)
        return consumption_values, time
    
    def chart_time_by_UAS(self):
        self.ax_time_by_UAS.clear()
        self.ax_time_by_UAS.set_title("Время тушения БАС с пожарным рукавом")
        self.ax_time_by_UAS.set_ylabel("Время тушения (с)")
        self.ax_time_by_UAS.set_xlabel("Конфигурация (Дрон / Рукав)")

        # Получить данные
        configs, times = self.time_by_UAS_hist()
        x = np.arange(len(configs))
        self.ax_time_by_UAS.bar(x, times, tick_label=configs)
        self.ax_time_by_UAS.set_xticklabels(configs, rotation=45, ha='right')
        self.figure_time_by_UAS.tight_layout()

    def time_by_UAS_hist(self):
        configs = []
        times = []
        t = 0
        for uav_idx in range(len(self.UAV_names)):
            self.hose_UAV_id = uav_idx + 1
            hose_UAV = UAV(self.hose_UAV_id)
            self.hose_UAV_hose_id = 1
            ea = EA(1, self.hose_UAV_hose_id)

            while (self.hose_UAV_hose_id < len(self.hose_names)) and (hose_UAV.payload < (ea.weight_per_meter() * self.height)):
                self.hose_UAV_hose_id += 1
                ea = EA(1, self.hose_UAV_hose_id)
            try:
                t = self.hose_UAV_fire_extinguishing_simulation()[0][-1] - self.time_extinguishing_start * 60
            except Exception:
                t = 0
            
            uav_name = self.UAV_names[uav_idx].name
            hose_name = self.hose_names[self.hose_UAV_hose_id - 1]
            configs.append(f"{uav_name} / {hose_name}")
            times.append(t)
        
        self.selected_hose_UAV_hose = self.hose_UAV_combobox.currentText()
        record = self.db.session.query(self.UAV_tablename).filter_by(name = self.selected_hose_UAV_hose).first()
        self.hose_UAV_id = getattr(record, 'id')
        self.hose_UAV_mass_label.setText(f"Масса дрона: {record.mass} кг")
        self.hose_UAV_payload_label.setText(f"Полезная нагрузка: {record.payload} кг")
        self.hose_UAV_flight_time_label.setText(f"Время полёта: {record.flight_time} мин")

        self.selected_hose_UAV_hose = self.hose_UAV_hose_combobox.currentText()
        record = self.db.session.query(self.hose_tablename).filter_by(name = self.selected_hose_UAV_hose).first()
        self.hose_UAV_hose_id = getattr(record, 'id')
        return configs, times
    