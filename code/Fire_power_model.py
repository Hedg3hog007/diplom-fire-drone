# Fire_power_model.py
import numpy as np
import math
from DroneFireModel import DataBase_data

class FireModel:
   
    db = DataBase_data()
    building_table = 'BUILDINGS_specification'

    def __init__(self, building_init_id: int, max_fire_area_init: int):
        self.building_id = building_init_id
        self.max_fire_area = max_fire_area_init
        self.name = self.db.record_get(self.building_table, building_init_id, 'name')
        self.lower_heat_value = self.db.record_get(self.building_table, building_init_id, 'lower_heat_value')
        self.flame_spread = self.db.record_get(self.building_table, building_init_id, 'flame_spread')
        self.burnout_speed = self.db.record_get(self.building_table, building_init_id, 'burnout_speed')
        self.fire_load_specific_mass = self.db.record_get(self.building_table, building_init_id, 'fire_load_specific_mass')
        self.coef_burn_completeness = self.db.record_get(self.building_table, building_init_id, 'coef_burn_completeness')
        self.heat_capacity_per_meter = self.db.record_get(self.building_table, building_init_id, 'heat_capacity_per_meter')
        self.time_max_power = ((2 * self.max_fire_area/(math.pi * self.flame_spread ** 2)) ** (1 / 2))
        self.time_burnout = (self.fire_load_specific_mass / self.burnout_speed)
        self.extinguished_area = 0
        self.fire_area = 0

    def fire_spread(self,  time: int):
        self.fire_area = math.pi / 2 * (self.flame_spread * time) ** 2  -  self.extinguished_area    
        Q_fire_spread = self.coef_burn_completeness * self.lower_heat_value * self.burnout_speed * self.fire_area

        return Q_fire_spread

    def fire_max_power(self):
        Q_fire_max_power = self.coef_burn_completeness * self.lower_heat_value * self.burnout_speed * (self.max_fire_area - self.extinguished_area)

        return Q_fire_max_power
    
    def fire_burnout(self, time: int):
        self.fire_area = self.max_fire_area - math.pi / 2 * (self.flame_spread * (time - self.time_burnout)) ** 2 - self.extinguished_area
        Q_fire_burnout = self.coef_burn_completeness * self.lower_heat_value * self.burnout_speed * self.fire_area

        return Q_fire_burnout
    
    def fire_calculate(self, time: int):
    # Расчёт мощности пожара в заданный момент времени
        if time < self.time_max_power:
            fire_power = self.fire_spread(time)
            return fire_power
        elif time < self.time_burnout:
            fire_power =  self.fire_max_power()
            return fire_power
        elif time >= self.time_burnout:
            fire_power =  self.fire_burnout(time)
            return fire_power
        
        