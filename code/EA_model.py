# EA_model.py
import math
from DroneFireModel import DataBase_data
from Fire_hose_model import Fire_hose

class EA:

    db = DataBase_data()
    fire_hose_table = 'FIRE_HOSE_specification'
    EA_table = 'EA_specification'

    def __init__(self, EA_id_init: int, fire_hose_id_init: int, height_init: int):
        self.EA_id = EA_id_init
        self.fire_hose_id = fire_hose_id_init
        self.height = height_init
        self.FireHose_diameter = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'diameter')
        self.pressure = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'pressure')
        self.EA_density = self.db.record_get(self.EA_table, EA_id_init, 'density')
        self.EA_viscosity = self.db.record_get(self.EA_table, EA_id_init, 'viscosity')
        self.EA_HeatCapacity = self.db.record_get(self.EA_table, EA_id_init, 'heat_capacity')
        self.EA_vape_HeatCapacity = self.db.record_get(self.EA_table, EA_id_init, 'vaporation_capacity')
        self.temperature_start = 20     # заглушка
        self.temperature_boiling = 100  # заглушка
        self.coef = 5                   # заглушка
        
    def EAConsumption (self):
        fire_hose = Fire_hose(self.FireHose_diameter, self.EA_density, self.EA_viscosity)
        self.pressure -= fire_hose.gravitation_loss_per_meter()
        if self.pressure <= 0:
            return 0
        else:
            EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt (2 * self.pressure / self.EA_density)
            self.pressure -= fire_hose.friction_loss_per_meter(EAConsumption)
            EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt(2 * self.pressure / self.EA_density)
        
        return EAConsumption

    def HeatAbsorption (self):
        EA_consumption = self.EAConsumption()
        # Q1 = EA_consumption * self.EA_density * (self.EA_HeatCapacity * (self.temperature_boiling - self.temperature_start))
        # EA_vape_rate = 1 / (1 + math.exp(-self.coef * ((Fire_power / Q1) - 1)))
        EA_vape_rate = 0  # заглушка
        HeatAbsorption = EA_consumption * self.EA_density * (self.EA_HeatCapacity * (self.temperature_boiling - self.temperature_start) + self.EA_vape_HeatCapacity * EA_vape_rate)
        return HeatAbsorption