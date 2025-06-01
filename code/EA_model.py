# EA_model.py
import math
from DroneFireModel import DataBase_data
from Fire_hose_model import Fire_hose

class EA:

    db = DataBase_data()
    fire_hose_table = 'Пожарные рукава'
    EA_table = 'Огнетушащие вещества'

    def __init__(self, EA_id_init: int, fire_hose_id_init: int):
        self.EA_id = EA_id_init
        self.fire_hose_id = fire_hose_id_init
        self.FireHose_diameter = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'diameter')
        self.pressure = self.db.record_get(self.fire_hose_table, fire_hose_id_init, 'pressure')
        self.EA_density = self.db.record_get(self.EA_table, EA_id_init, 'density')
        self.EA_viscosity = self.db.record_get(self.EA_table, EA_id_init, 'viscosity')
        self.EA_HeatCapacity = self.db.record_get(self.EA_table, EA_id_init, 'heat_capacity')
        self.temperature_start = 20     
        self.temperature_boiling = 100  
        self.length = 0.5
        
    def EAConsumption (self):
        fire_hose = Fire_hose(self.fire_hose_id)
        for i in range(round(1 / self.length)):
            self.pressure -= fire_hose.gravitation_loss_per_length(self.EA_density, self.length)
            if self.pressure <= 0:
                return 0
            else:
                EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt (2 * self.pressure / self.EA_density)
                self.pressure -= fire_hose.friction_loss_per_length(self.EA_density, EAConsumption, self.EA_viscosity, self.length)
                if self.pressure <= 0:
                    return 0
                EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt(2 * self.pressure / self.EA_density)
        
        return EAConsumption

    def HeatAbsorption (self):
        HeatAbsorption = self.EAConsumption() * self.EA_density * (self.EA_HeatCapacity * (self.temperature_boiling - self.temperature_start))
        return HeatAbsorption
    
    def weight_per_meter (self):
        water_weight = math.pi * self.EA_density * (self.FireHose_diameter / 2) ** 2
        hose_weight = Fire_hose(self.fire_hose_id).weight_per_meter()
        weight = water_weight + hose_weight
        return weight
    
    def EAConsumption_Reynolds (self):
        fire_hose = Fire_hose(self.fire_hose_id)
        if self.pressure <= 0:
            return 0, 0, 0, 0
        else:
            EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt (2 * self.pressure / self.EA_density)
            friction_loss = fire_hose.friction_loss_per_length(self.EA_density, EAConsumption, self.EA_viscosity, self.length)
            self.pressure -= friction_loss
            if self.pressure <= 0:
                return 0, 0, 0, 0
            EAConsumption = math.pi * (self.FireHose_diameter / 2) ** 2 * math.sqrt(2 * self.pressure / self.EA_density)
            
        return fire_hose.Reynolds, fire_hose.friction_coef, friction_loss, EAConsumption

    def HeatAbsorption_tank(self, consumption):
        HeatAbsorption = consumption * self.EA_density * (self.EA_HeatCapacity * (self.temperature_boiling - self.temperature_start))
        return HeatAbsorption