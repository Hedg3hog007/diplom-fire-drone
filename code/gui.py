# gui.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QComboBox, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from DroneFireModel import DataBase_data
from Fire_power_model import FireModel
from EA_model import EA
import numpy as np

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Динамическая модель тушения пожаров")
        self.setGeometry(100, 100, 1000, 800)

        # Создание основного виджета
        self.main_widget = QWidget()
        self.layout = QHBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # График интенсивности пожара
        self.left_layout = QVBoxLayout()
        self.figure_fire = Figure(figsize=(6, 4), dpi=100)
        self.canvas_fire = FigureCanvas(self.figure_fire)
        self.ax_fire = self.figure_fire.add_subplot(111)
        self.line, = self.ax_fire.plot([], [], label="Мощность тепловыделения, Дж/с")
        self.ax_fire.legend(loc = 'upper left')
        self.ax_fire.set_title("Развитие пожара")
        self.ax_fire.set_xlabel("Время (с)")
        self.ax_fire.set_ylabel("Интенсивность пожара (Дж/с)")
        self.left_layout.addWidget(self.canvas_fire)
        self.layout.addLayout(self.left_layout)

        # График интенсивности тушения
        self.right_layout = QVBoxLayout()
        self.figure_hose = Figure(figsize=(6, 4), dpi=100)
        self.canvas_hose = FigureCanvas(self.figure_hose)
        self.ax_hose = self.figure_hose.add_subplot(111)
        self.ax_hose.set_title("Зависимость интенсивности тушения от высоты")
        self.ax_hose.set_xlabel("Высота тушения (м)")
        self.ax_hose.set_ylabel("Интенсивность тушения (МДж/с)")
        self.right_layout.addWidget(self.canvas_hose)
        self.layout.addLayout(self.right_layout)

        # Инициализация начальных параметров
        self.area = 60  # Начальная площадь помещения
        self.height = 60 # Начальная высота тушения
        self.db = DataBase_data()

        self.hose_names = [] # Список названий пожарных рукавов
        self.hose_tablename = self.db._models.get('FIRE_HOSE_specification')
        for i in range (len(self.db.session.query(self.hose_tablename).all())):
            self.hose_names.append(self.db.record_get('FIRE_HOSE_specification', i + 1, 'name'))

        self.selected_hose_UAV_hose = self.hose_names[0] # Начальный тип рукава
        self.hose_UAV_hose_id = 1 
        self.selected_tank_UAV_hose = self.hose_names[0]
        self.tank_UAV_hose_id = 1
 
        # Список типов помещений из базы данных
        self.buildings_tablename = self.db._models.get('BUILDINGS_specification')
        self.buildings_names = self.db.session.query(self.buildings_tablename.name).all()

        self.selected_building = self.buildings_names[0] # Начальный тип помещения
        self.building_id = 1 

        # Список дронов из базы данных
        self.UAV_tablename = self.db._models.get('UAV_specification')
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

    def create_input_layout(self):
        self.parameters_layout = QVBoxLayout()
        self.left_layout.addLayout(self.parameters_layout)

    def create_sliders(self):
        """Создает слайдеры для управления параметрами."""
        def create_slider(label_text, min_val, max_val, default_val, callback, object_name):
            slider_layout = QVBoxLayout()

            label = QLabel(f"{label_text} ({default_val})")
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

        # Создание слайдера для площади помещения
        area_slider = create_slider(
            label_text="Площадь помещения",
            min_val=1,
            max_val=100,
            default_val=self.area,
            callback = self.area_changed,
            object_name="area_slider"
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
        self.UAV_var_layout = QHBoxLayout()
        self.parameters_layout.addLayout(self.UAV_var_layout)

        self.hose_UAV_main_layout = QVBoxLayout()
        self.tank_UAV_main_layout = QVBoxLayout()

        self.UAV_var_layout.addLayout(self.hose_UAV_main_layout)
        self.UAV_var_layout.addLayout(self.tank_UAV_main_layout)

        self.hose_UAV_main_layout.addWidget(QLabel('Прицепной пожарный рукав'))
        self.tank_UAV_main_layout.addWidget(QLabel('Бортовой резервуар'))

    def create_hose_UAV_hose_combobox(self):
        
        uav_combo_layout = QVBoxLayout()
                          
        # Метка для списка
        label = QLabel("Тип рукава:")
        uav_combo_layout.addWidget(label)

        # Создание QComboBox
        self.hose_combobox = QComboBox()
        self.hose_combobox.addItems(self.hose_names)
        self.hose_combobox.currentTextChanged.connect(self.hose_UAV_hose_combobox_changed)
        uav_combo_layout.addWidget(self.hose_combobox)

        # Добавление в макет
        self.hose_UAV_main_layout.addLayout(uav_combo_layout)

    def create_tank_UAV_hose_combobox(self):
        tank_uav_combo_layout = QVBoxLayout()
                          
        # Метка для списка
        label = QLabel("Тип рукава для бортового ОТВ:")
        tank_uav_combo_layout.addWidget(label)

        # Создание QComboBox
        self.hose_combobox = QComboBox()
        self.hose_combobox.addItems(self.hose_names)
        self.hose_combobox.currentTextChanged.connect(self.tank_UAV_hose_combobox_changed)
        tank_uav_combo_layout.addWidget(self.hose_combobox)

        # Добавление в макет
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
        self.tank_UAV_main_layout.addWidget(self.tank_UAV_fire_extinguishing_time_label)

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
        self.hose_UAV_main_layout.addWidget(self.hose_UAV_fire_extinguishing_time_label)

    def buildings_combobox_changed(self, text):
        self.selected_building = text  
        # Обновление ID выбранного здания по имени
        record = self.db.session.query(self.buildings_tablename).filter_by(name = self.selected_building).first()
        self.building_id = getattr(record, 'id')
        self.update_graph()

    def hose_UAV_combobox_changed(self, text):
        self.selected_hose_UAV_hose = text
        # Обновление ID выбранного дрона по имени
        record = self.db.session.query(self.UAV_tablename).filter_by(name = self.selected_hose_UAV_hose).first()
        self.hose_UAV_id = getattr(record, 'id')
        self.hose_UAV_mass_label.setText(f"Масса дрона: {record.mass} кг")
        self.hose_UAV_payload_label.setText(f"Полезная нагрузка: {record.payload} кг")
        self.hose_UAV_flight_time_label.setText(f"Время полёта: {record.flight_time} мин")
        self.update_graph()

    def tank_UAV_combobox_changed(self, text):
        self.selected_tank_UAV_hose = text
        # Обновление ID выбранного дрона по имени
        record = self.db.session.query(self.UAV_tablename).filter_by(name = self.selected_tank_UAV_hose).first()
        self.tank_UAV_id = getattr(record, 'id')
        self.tank_UAV_mass_label.setText(f"Масса дрона: {record.mass} кг")
        self.tank_UAV_payload_label.setText(f"Полезная нагрузка: {record.payload} кг")
        self.tank_UAV_flight_time_label.setText(f"Время полёта: {record.flight_time} мин")
        self.update_graph()

    def hose_UAV_hose_combobox_changed(self, text):
        self.selected_hose_UAV_hose = text
        # Обновление ID выбранного рукава по имени
        record = self.db.session.query(self.hose_tablename).filter_by(name = self.selected_hose_UAV_hose).first()
        self.hose_UAV_hose_id = getattr(record, 'id')
        self.update_graph()

    def tank_UAV_hose_combobox_changed(self, text):
        self.selected_tank_UAV_hose = text
        # Обновление ID выбранного рукава по имени
        record = self.db.session.query(self.hose_tablename).filter_by(name = self.selected_tank_UAV_hose).first()
        self.tank_UAV_hose_id = getattr(record, 'id')
        self.update_graph()
   
    def area_changed(self, value):
        self.area = value
        self.update_graph()

    def height_changed(self, text, label):
        self.height = int(text)
        if self.height < 0:
            self.height = 0
        label.setText(f"Высота тушения (м): {self.height}")
        self.update_graph()
   
    def update_label(self, label, value):
        label.setText(f"{label.text().split('(')[0].strip()} ({value})")

    def update_graph(self):
        # Обновление графика развития пожара
        area_slider = self.findChild(QSlider, "area_slider")
        self.area = area_slider.value()
        self.ax_fire.clear()
        x, y = self.natural_fire_spread()
        self.ax_fire.plot(x, y,  label = "Натуральное развитие пожара")

        # Обновление графика противодействия пожару
        x_ext, y_ext = self.hose_UAV_fire_extinguishing_simulation()
        x_ext_tank_uav, y_ext_tank_uav = self.tank_UAV_fire_extinguishing_simulation()
        self.ax_fire.set_title("Развитие пожара")
        self.ax_fire.set_xlabel("Время (с)")
        self.ax_fire.set_ylabel("Интенсивность пожара (Дж/с)")
        self.ax_fire.plot(x_ext, y_ext, label="прицепной рукав")
        self.ax_fire.plot(x_ext_tank_uav, y_ext_tank_uav, label="бортовой резервуар")

        self.ax_fire.legend(loc = 'upper left')

        # Отображаем график
        self.ax_fire.relim()
        self.ax_fire.autoscale_view()
        self.canvas_fire.draw()

        # Обновление графика интенсивности тушения
        heights = np.linspace(0, self.height, self.height)
                
        # Очистка графика
        self.ax_hose.clear()
        self.ax_hose.set_title("Интенсивность тушения от высоты")
        self.ax_hose.set_xlabel("Высота тушения (м)")
        self.ax_hose.set_ylabel("Интенсивность тушения (Дж/с)")

        # Рассчитываем и отображаем линии для каждого типа рукава
        for i in range (len(self.hose_names)):
            intensities = self.calculate_hose_intensities(heights, hose_id = i + 1)
            self.ax_hose.plot(heights, intensities, label = self.hose_names[i])

        # Добавляем линию максимальной мощности пожара
        max_fire_plot = np.linspace(self.max_fire_power, self.max_fire_power, len(heights))
        self.ax_hose.plot(heights, max_fire_plot, label = "Макс. мощность пожара", linestyle='--', color='red')

        # Добавляем легенду
        self.ax_hose.legend(loc = 'upper right')

        # Перерисовываем график
        self.ax_hose.relim()
        self.ax_hose.autoscale_view()
        self.canvas_hose.draw()

    def calculate_hose_intensities(self, heights, hose_id):
        ea_model = EA(1, hose_id, self.height)
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
        # Инициализация параметров для моделирования тушения
        import random
        self.time_extinguishing_start = random.randint(8 * 60, 13 * 60)
        y = np.array([])
        time = 0
        fire_power = 0
        ea_model = EA(1, self.hose_UAV_hose_id, self.height)
        for i in range (self.height):
            EA_power = ea_model.HeatAbsorption()

        hose_UAV_fire_model = FireModel(self.building_id, self.area)

        # Моделирование тушения
        while (hose_UAV_fire_model.max_fire_area - hose_UAV_fire_model.extinguished_area > 0) and (fire_power >= 0):

            # Развитие пожара до начала тушения
            if time < self.time_extinguishing_start:
                y = np.append(y, hose_UAV_fire_model.fire_calculate(time))
                fire_power = y[-1]
                time += 1

            # Тушение пожара
            else:
                y = np.append(y, hose_UAV_fire_model.fire_calculate(time))
                fire_power = y[-1]
                fire_power_per_meter = fire_power / (self.area - hose_UAV_fire_model.extinguished_area)
                if fire_power_per_meter < EA_power:
                    burning_temperature = 1000
                    while burning_temperature > 230:
                        delta_temperature = (EA_power - fire_power_per_meter) / hose_UAV_fire_model.heat_capacity_per_meter
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


        hose_UAV_fire_extinguishing_time = time - self.time_extinguishing_start
        self.hose_UAV_fire_extinguishing_time_label.setText(f"Пожар потушен за {hose_UAV_fire_extinguishing_time // 60} мин {hose_UAV_fire_extinguishing_time % 60} сек")
        self.hose_UAV_fire_extinguishing_time_label.setStyleSheet('background-color: lightgreen')

        x = np.linspace(0, time, time)
        return x, y

    def tank_UAV_fire_extinguishing_simulation(self):
        from UAV_model import UAV
        
        # Инициализация переменных
        tank_UAV_model = UAV(self.tank_UAV_id) # создать список дронов
        EA_model = EA(1, self.tank_UAV_hose_id, height_init = self.height) 
        EA_power = EA_model.HeatAbsorption()
        time = 0
        current_flight_time = 0
        time_start = self.time_extinguishing_start + tank_UAV_model.service_time() + tank_UAV_model.lift_time(self.height) 
        fire_power = 0
        y = np.array([])
        tank_UAV_fire_model = FireModel(self.building_id, self.area)

        for i in range (time_start):
            y = np.append(y, tank_UAV_fire_model.fire_calculate(time))
            time += 1

        while (tank_UAV_fire_model.max_fire_area - tank_UAV_fire_model.extinguished_area > 0) and (fire_power) >= 0:
            
            # Тушение пожара
            UAV_EA_volume = tank_UAV_model.payload / EA_model.EA_density
            for i in range (round(UAV_EA_volume / EA_model.EAConsumption())):
                y = np.append(y, tank_UAV_fire_model.fire_calculate(time))
                fire_power = y[-1]
                fire_power_per_meter = fire_power / (self.area - tank_UAV_fire_model.extinguished_area)
                if (tank_UAV_fire_model.max_fire_area - tank_UAV_fire_model.extinguished_area <= 0) or (fire_power) < 0:
                    tank_UAV_fire_extinguishing_time = time - self.time_extinguishing_start
                    self.tank_UAV_fire_extinguishing_time_label.setStyleSheet("background-color: lightgreen")
                    self.tank_UAV_fire_extinguishing_time_label.setText(f"Пожар потушен за {tank_UAV_fire_extinguishing_time // 60} мин {tank_UAV_fire_extinguishing_time % 60} сек")
                    time += 1
                    x = np.linspace(0, time, time)
                    return x, y
                if fire_power_per_meter < EA_power:
                    burning_temperature = 1000
                    while burning_temperature > 230:
                        delta_temperature = (EA_power - fire_power_per_meter) / tank_UAV_fire_model.heat_capacity_per_meter
                        burning_temperature -= delta_temperature
                        time += 1
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


            if (tank_UAV_model.flight_time * 60) < (current_flight_time + tank_UAV_model.lift_time(self.height) + tank_UAV_model.descend_time(self.height)):
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
        
        self.tank_UAV_fire_extinguishing_time_label.setText("Пожар не потушен")
        self.tank_UAV_fire_extinguishing_time_label.setStyleSheet('background-color: lightcoral')

        x = np.linspace(0, time, time)
        return x, y        