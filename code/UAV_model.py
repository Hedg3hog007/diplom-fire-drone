# UAV_model.py
import math
from DroneFireModel import DataBase_data

class UAV:
    db = DataBase_data()
    UAV_spec_table = 'Дроны'
    
    def __init__(self, UAV_id_init: int):
        self.UAV_id = UAV_id_init
        self.mass = self.db.record_get(self.UAV_spec_table, UAV_id_init, 'mass')
        self.payload = self.db.record_get(self.UAV_spec_table, UAV_id_init, 'payload')
        self.flight_time = self.db.record_get(self.UAV_spec_table, UAV_id_init, 'flight_time')
        self.lift_velocity = 4 
        self.descend_velocity = 4 
        

    def lift_time(self, height: int):
        lift_time = height / self.lift_velocity
        return round(lift_time)
    
    def descend_time(self, height: int):
        descend_time = height / self.descend_velocity
        return round(descend_time)
    
    def service_time(self):
        return 210          # Время обслуживания 3.5 минуты
    
    def EA_refill_time(self):
        EA_refill_time = self.payload / 7 # заправка 7 л/с
        return round(EA_refill_time)    