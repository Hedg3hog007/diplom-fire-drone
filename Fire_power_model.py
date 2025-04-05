# Fire_power_model.py
import numpy as np
import math
from DroneFireModel import DataBase_data

class FireModel:
    def calculate(self, amplitude, frequency):
        x = np.linspace(0, 10, 500)
        y = amplitude * np.sin(frequency * x)
        return x, y
    

    flame_spread = float()
    lower_heat_value = int()
    burnout_speed = float()
    fire_load_specific_mass = int()
    time = int()
    coef_burn_completeness = float()

    db = DataBase_data()
    building_table = 'BUILDINGS_specification'
    building_id = int()

    def __init__(self, building_init_id, max_fire_area_init):
        self.building_id = building_init_id
        

    def fire_spread(flame_spread, coef_burn_completeness, lower_heat_value, burnout_speed, time):
        fire_area = math.pi * (flame_spread * time/ 1.4) ** 2      
        Q_fire_spread = coef_burn_completeness * lower_heat_value * burnout_speed * fire_area

        return Q_fire_spread

    def fire_max_power(coef_burn_completeness, lower_heat_value, burnout_speed, Smax):
        Q_fire_max_power = coef_burn_completeness * lower_heat_value * burnout_speed * Smax

        return Q_fire_max_power
    
    def fire_burnout(fire_load_specific_mass, burnout_speed, Smax, flame_spread, time, coef_burn_completeness, lower_heat_value):
        time_2 = fire_load_specific_mass / burnout_speed
        fire_area = Smax - math.pi * (flame_spread * (time - time_2)) ** 2
        Q_fire_burnout = coef_burn_completeness * lower_heat_value * burnout_speed * fire_area

        return Q_fire_burnout






