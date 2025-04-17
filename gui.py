# gui.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QLabel, QComboBox, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from DroneFireModel import DataBase_data
from Fire_power_model import FireModel
import numpy as np

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Динамическая модель тушения пожаров")
        self.setGeometry(100, 100, 1000, 500)

        # Создание основного виджета
        self.main_widget = QWidget()
        self.layout = QHBoxLayout(self.main_widget)
        self.setCentralWidget(self.main_widget)

        # График интенсивности пожара
        self.fire_layout = QVBoxLayout()
        self.figure_fire = Figure(figsize=(6, 4), dpi=100)
        self.canvas_fire = FigureCanvas(self.figure_fire)
        self.ax_fire = self.figure_fire.add_subplot(111)
        self.line, = self.ax_fire.plot([], [], label="Мощность тепловыделения, Дж/с")
        self.ax_fire.legend()
        self.ax_fire.set_title("Развитие пожара")
        self.ax_fire.set_xlabel("Время (с)")
        self.ax_fire.set_ylabel("Интенсивность пожара (Дж/с)")
        self.fire_layout.addWidget(self.canvas_fire)
        self.layout.addLayout(self.fire_layout)

        # График интенсивности тушения
        self.EA_layout = QVBoxLayout()
        self.figure_hose = Figure(figsize=(6, 4), dpi=100)
        self.canvas_hose = FigureCanvas(self.figure_hose)
        self.ax_hose = self.figure_hose.add_subplot(111)
        self.ax_hose.set_title("Зависимость интенсивности тушения от высоты")
        self.ax_hose.set_xlabel("Высота тушения (м)")
        self.ax_hose.set_ylabel("Интенсивность тушения (МДж/с)")
        self.EA_layout.addWidget(self.canvas_hose)
        self.layout.addLayout(self.EA_layout)

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

            self.fire_layout.addLayout(slider_layout)
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
        self.fire_layout.addLayout(combo_layout)

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
        self.EA_layout.addLayout(height_layout)

    def update_height(self, text, label):
        self.height = int(text)
        if self.height < 0:
            self.height = 0
        label.setText(f"Высота тушения (м): {self.height}")
        self.update_graph()
   
    def update_label(self, label, value):
        label.setText(f"{label.text().split('(')[0].strip()} ({value})")

    def update_graph(self):

        # Обновление первого графика
        area_slider = self.findChild(QSlider, "area_slider")
        self.area = area_slider.value()
        x, y = self.calculate_fire()
        self.line.set_data(x, y)
        self.ax_fire.relim()
        self.ax_fire.autoscale_view()
        self.canvas_fire.draw()

        # Обновление второго графика
        heights = np.linspace(0, self.height, self.height)
        
        hose_names = []
        for i in range (len(self.db.session.query(self.db._models.get('FIRE_HOSE_specification')).all())):
            hose_names.append(self.db.record_get('FIRE_HOSE_specification', i + 1, 'name'))
        
        # Очистка графика/
        self.ax_hose.clear()
        self.ax_hose.set_title("Интенсивность тушения от высоты")
        self.ax_hose.set_xlabel("Высота тушения (м)")
        self.ax_hose.set_ylabel("Интенсивность тушения (Дж/с)")

        # Рассчитываем и отображаем линии для каждого типа рукава
        for i in range (len(hose_names)):
            intensities = self.calculate_hose_intensities(heights, hose_id = i + 1)
            self.ax_hose.plot(heights, intensities, label = hose_names[i])

        # Добавляем линию максимальной мощности пожара
        max_fire_plot = []
        for h in heights:
            max_fire_plot.append(self.max_fire_power)
        self.ax_hose.plot(heights, max_fire_plot, label = "Макс. мощность пожара", linestyle='--', color='red')

        # Добавляем легенду
        self.ax_hose.legend()

        # Перерисовываем график
        self.ax_hose.relim()
        self.ax_hose.autoscale_view()
        self.canvas_hose.draw()

    def calculate_hose_intensities(self, heights, hose_id):
        from EA_model import EA
        ea = EA(1, hose_id, self.height)
        intensities = []
        for h in heights:
            intensities.append(ea.HeatAbsorption())

        return intensities 


    def calculate_fire(self):

        model_class = self.db._models.get('BUILDINGS_specification')
        record = self.db.session.query(model_class).filter_by(name = self.selected_building).first()
        self.building_id = getattr(record, 'id')
        fire_model = FireModel(self.building_id, self.area)
        self.max_fire_power = fire_model.fire_max_power()
           
        return fire_model.fire_calculate()
  
            