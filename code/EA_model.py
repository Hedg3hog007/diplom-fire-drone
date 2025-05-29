# EA_model.py
import math
from DroneFireModel import DataBase_data
from Fire_hose_model import Fire_hose

class EA:

    db = DataBase_data()
    fire_hose_table = 'FIRE_HOSE_specification'
    EA_table = 'EA_specification'

    def __init__(self, EA_id_init: int, fire_hose_id_init: int):
        self.EA_id = EA_id_init
        self.fire_hose_id = fire_hose_id_init
        self.FireHose_diameter = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'diameter')
        self.pressure = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'pressure')
        self.EA_density = self.db.record_get(self.EA_table, EA_id_init, 'density')
        self.EA_viscosity = self.db.record_get(self.EA_table, EA_id_init, 'viscosity')
        self.EA_HeatCapacity = self.db.record_get(self.EA_table, EA_id_init, 'heat_capacity')
        self.temperature_start = 20     # заглушка
        self.temperature_boiling = 100  # заглушка
        self.coef = 5                   # заглушка
        
    def EAConsumption (self):
        fire_hose = Fire_hose(self.fire_hose_id)
        self.pressure -= fire_hose.gravitation_loss_per_meter(self.EA_density)
        if self.pressure <= 0:
            return 0
        else:
            EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt (2 * self.pressure / self.EA_density)
            # self.pressure -= fire_hose.friction_loss_per_meter(self.EA_density, EAConsumption, self.EA_viscosity)
            # if self.pressure <= 0:
            #     return 0
            # EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt(2 * self.pressure / self.EA_density)
        
        return EAConsumption

    def HeatAbsorption (self):
        HeatAbsorption = self.EAConsumption() * self.EA_density * (self.EA_HeatCapacity * (self.temperature_boiling - self.temperature_start))
        return HeatAbsorption
    
    def weight_per_meter (self):
        weight = math.pi * self.EA_density * (self.FireHose_diameter / 2) ** 2 
        return weight