# Fire_power_model.py
import numpy as np
import math
from DroneFireModel import DataBase_data

class FireModel:
   
    lower_heat_value = int()
    flame_spread = float()
    burnout_speed = float()
    fire_load_specific_mass = int()
    coef_burn_completeness = float()
    max_fire_area = int()
    time_max_power = float()
    time_burnout = float()

    db = DataBase_data()
    building_table = 'BUILDINGS_specification'
    building_id = int()

    def __init__(self, building_init_id: int, max_fire_area_init: int):
        self.building_id = building_init_id
        self.max_fire_area = max_fire_area_init
        self.name = self.db.record_get(self.building_table, building_init_id, 'name')
        self.lower_heat_value = self.db.record_get(self.building_table, building_init_id, 'lower_heat_value')
        self.flame_spread = self.db.record_get(self.building_table, building_init_id, 'flame_spread')
        self.burnout_speed = self.db.record_get(self.building_table, building_init_id, 'burnout_speed')
        self.fire_load_specific_mass = self.db.record_get(self.building_table, building_init_id, 'fire_load_specific_mass')
        self.coef_burn_completeness = self.db.record_get(self.building_table, building_init_id, 'coef_burn_completeness')
        self.time_max_power = ((2 * self.max_fire_area/(math.pi * self.flame_spread ** 2)) ** (1 / 2))
        self.time_burnout = (self.fire_load_specific_mass / self.burnout_speed)
        

    def fire_spread(self,  time: int):
        fire_area = math.pi / 2 * (self.flame_spread * time) ** 2      
        Q_fire_spread = self.coef_burn_completeness * self.lower_heat_value * self.burnout_speed * fire_area

        return Q_fire_spread

    def fire_max_power(self):
        Q_fire_max_power = self.coef_burn_completeness * self.lower_heat_value * self.burnout_speed * self.max_fire_area

        return Q_fire_max_power
    
    def fire_burnout(self, time: int):
        fire_area = self.max_fire_area - math.pi / 2 * (self.flame_spread * (time - self.time_burnout)) ** 2
        Q_fire_burnout = self.coef_burn_completeness * self.lower_heat_value * self.burnout_speed * fire_area

        return Q_fire_burnout
    
    def fire_calculate(self):
        time = 0
        fire_power = 0
        y = np.array([])
        while fire_power >= 0:
            time += 1
            if time < self.time_max_power:
                y = np.append(y, self.fire_spread(time))
            elif time < self.time_burnout:
                y = np.append(y, self.fire_max_power())
            elif time >= self.time_burnout:
                y = np.append(y, self.fire_burnout(time))
                fire_power = self.fire_burnout(time)

        x = np.linspace(0, time, time)        
        return x, y
        
        