# gui.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QComboBox, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from DroneFireModel import DataBase_data
from Fire_power_model import FireModel

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Динамическая модель тушения пожаров")
        self.setGeometry(100, 100, 800, 600)

        # Создание основного виджета
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # Создание графика
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [], label="Мощность тепловыделения, Дж/с")
        self.ax.legend()
        self.ax.set_title("Развитие пожара")
        self.ax.set_xlabel("Время (с)")
        self.ax.set_ylabel("Интенсивность горения")
        self.layout.addWidget(self.canvas)

        # Инициализация параметров
        self.area = 50
        self.height = 100
        self.selected_building = "Паркинг"
        self.building_id = 1
        self.db = DataBase_data()

        # Создание полей ввода
        self.create_sliders()
        self.create_combobox()
        self.create_height_input()

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

            self.layout.addLayout(slider_layout)
            return slider

        # Создание слайдера для площади помещения
        area_slider = create_slider(
            label_text="Площадь помещения",
            min_val=1,
            max_val=100,
            default_val=self.area,
            callback=self.update_graph,
            object_name="area_slider"
        )

    def create_combobox(self):

        combo_layout = QVBoxLayout()
        
        # Список типов помещений из базы данных
        db = DataBase_data()
        model_class = db._models.get('BUILDINGS_specification')
        results = db.session.query(model_class.name).all()
           
        # Метка для списка
        label = QLabel("Тип помещения:")
        combo_layout.addWidget(label)

        # Создание QComboBox
        self.combobox = QComboBox()
        self.combobox.addItems([(result.name) for result in results])
        self.combobox.currentTextChanged.connect(self.on_combobox_changed)  # Обработчик события
        combo_layout.addWidget(self.combobox)

        # Добавление в макет
        self.layout.addLayout(combo_layout)

    def on_combobox_changed(self, text):
        self.selected_building = text  
        self.update_graph()  


    def create_height_input(self):

        height_layout = QVBoxLayout()

        # Метка для поля ввода
        label = QLabel(f"Высота тушения (м): {self.height}")
        height_layout.addWidget(label)
        self.height_input = QLineEdit(str(self.height))
        self.height_input.setPlaceholderText("Введите высоту (м)")  # Подсказка
        self.height_input.textChanged.connect(lambda text: self.update_height(text, label)) # Обработчик события
        height_layout.addWidget(self.height_input)

        # Добавление в макет
        self.layout.addLayout(height_layout)

    def update_height(self, text, label):
        self.height = int(text)
        if self.height < 0:
            self.height = 0
        label.setText(f"Высота тушения (м): {self.height}")
        self.update_graph()
    

    def update_label(self, label, value):
        label.setText(f"{label.text().split('(')[0].strip()} ({value})")

    def update_graph(self):
        area_slider = self.findChild(QSlider, "area_slider")
        
        if area_slider is None:
            return
        self.area = area_slider.value()
        
        x, y = self.calculate_fire()
        self.line.set_data(x, y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def calculate_fire(self):
        
        import numpy as np

        model_class = self.db._models.get('BUILDINGS_specification')
        record = self.db.session.query(model_class).filter_by(name = self.selected_building).first()
        self.building_id = getattr(record, 'id')
        fire_model = FireModel(self.building_id, self.area)
        fire_max_power = fire_model.fire_max_power()
        print ("Максимальная мощность пожара: ",  fire_max_power / 1000000, " МДж/с")
        self.calculate_EA(fire_max_power)
           
        return fire_model.fire_calculate()
    
    def calculate_EA(self, fire_max_power):

        from EA_model import EA
        model_class = self.db._models.get('FIRE_HOSE_specification')
        results = self.db.session.query(model_class).all()
        for i in range(len(results)):
            ea = EA(1,i + 1, self.height)
            ea_heat_absorption = ea.HeatAbsorption(fire_max_power)
            record = self.db.session.query(model_class).filter_by(id = i + 1).first()
            if ea_heat_absorption > fire_max_power:
                print(getattr(record, 'name'), 'может. ', ea_heat_absorption / 1000000, ' МДж/с' )
            else:
                print(getattr(record, 'name'), 'не может. ', ea_heat_absorption / 1000000, ' МДж/с' )
                
                
            