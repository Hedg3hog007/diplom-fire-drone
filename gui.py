# gui.py
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider, QLabel, QPushButton
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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
        self.line, = self.ax.plot([], [], label="Модель")
        self.ax.legend()
        self.ax.set_title("График модели")
        self.ax.set_xlabel("Время (с)")
        self.ax.set_ylabel("Интенсивность горения")
        self.layout.addWidget(self.canvas)

        # Инициализация параметров
        self.amplitude = 1
        self.frequency = 1

        # Создание слайдеров
        self.create_sliders()

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

        # Создание слайдера для амплитуды
        amplitude_slider = create_slider(
            label_text="Амплитуда",
            min_val=1,
            max_val=10,
            default_val=self.amplitude,
            callback=self.update_graph,
            object_name="amplitude_slider"
        )

        # Создание слайдера для частоты
        frequency_slider = create_slider(
            label_text="Частота",
            min_val=1,
            max_val=10,
            default_val=self.frequency,
            callback=self.update_graph,
            object_name="frequency_slider"
        )

    def update_label(self, label, value):
        """Обновляет текст метки слайдера."""
        label.setText(f"{label.text().split('(')[0].strip()} ({value})")

    def update_graph(self):
        """Обновляет данные графика."""
        amplitude_slider = self.findChild(QSlider, "amplitude_slider")
        frequency_slider = self.findChild(QSlider, "frequency_slider")

        if amplitude_slider is None or frequency_slider is None:
            return

        self.amplitude = amplitude_slider.value()
        self.frequency = frequency_slider.value()

        # Здесь можно вызвать внешнюю модель для расчета данных
        x, y = self.calculate_data(self.amplitude, self.frequency)
        self.line.set_data(x, y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def calculate_data(self, amplitude, frequency):
        """Метод для расчета данных"""
        
        import numpy as np
        from Fire_power_model import FireModel
        fire_model = FireModel(1, 50)
        return fire_model.fire_calculate()
    
        