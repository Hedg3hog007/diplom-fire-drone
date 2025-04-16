# EA_model.py
import math
from DroneFireModel import DataBase_data

class EA:

    EA_id = int()
    fire_hose_id = int()
    FireHose_diameter = float()
    pressure = int()
    EA_density = int()
    EA_HeatCapacity = int()
    EA_vape_HeatCapacity = int()


    db = DataBase_data()
    fire_hose_table = 'FIRE_HOSE_specification'
    EA_table = 'EA_specification'

    def __init__(self, EA_id_init, fire_hose_id_init):
        self.EA_id = EA_id_init
        self.fire_hose_id = fire_hose_id_init
        self.FireHose_diameter = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'diameter')
        self.pressure = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'pressure')
        self.EA_density = self.db.record_get(self.EA_table, EA_id_init, 'density')
        self.EA_HeatCapacity = self.db.record_get(self.EA_table, EA_id_init, 'heat_capacity')
        self.EA_vape_HeatCapacity = self.db.record_get(self.EA_table, EA_id_init, 'vaporation_capacity')
        self.temperature_start = 20     # заглушка
        self.temperature_boiling = 100  # заглушка
        self.coef = 5                   # заглушка
        
       

    def EAConsumption (self):
        # давление будет изменяться от высоты. пока оно статично

        EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt(2 * self.pressure / self.EA_density)
        return EAConsumption

    def HeatAbsorption (self):
        # сюда ещё передаётся мощность пожара Fire_power. пока это не учитывается

        consump = self.EAConsumption()
        Q1 = consump * self.EA_density * (self.EA_HeatCapacity * (self.temperature_boiling - self.temperature_start))
        # EA_vape_rate = 1 / (1 + math.exp(-self.coef * ((Fire_power/Q1)-1)))
        EA_vape_rate = 0 # заглушка
        HeatAbsorption = consump * self.EA_density * (self.EA_HeatCapacity * (self.temperature_boiling - self.temperature_start) + self.EA_vape_HeatCapacity * EA_vape_rate)
        return HeatAbsorption

