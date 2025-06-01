# Fire_hose_model.py
import math
from DroneFireModel import DataBase_data

air_density = 1.293
g = 9.81

class Fire_hose:   
    db = DataBase_data()
    fire_hose_table = 'Пожарные рукава'

    def __init__ (self, fire_hose_init_id):
        self.fire_hose_id = fire_hose_init_id
        self.diameter = self.db.record_get(self.fire_hose_table, fire_hose_init_id, 'diameter')
        self.specific_mass = self.db.record_get(self.fire_hose_table, fire_hose_init_id, 'specific_mass')

    def gravitation_loss_per_length(self, EA_density, length):
        gravitation_loss  = (EA_density - air_density) * g * length
        return gravitation_loss
    
    
    def friction_loss_per_length (self, EA_density, EA_consumption, EA_viscosity, length):
        return 0
        self.Reynolds = (4 * EA_density * EA_consumption) / (math.pi * EA_viscosity * self.diameter)
        # self.friction_coef = ( (64/self.Reynolds)**8 + 9.5 * (math.log10(0.000025 /(3.7*self.diameter) + 5.74/(self.Reynolds**0.9)) - (2500/self.Reynolds)**6 )**-16 )**(1/8)

        if self.Reynolds > 2320:
            epsilon = 0.000025  # pipe roughness
            A0 = -0.79638 * math.log((epsilon / self.diameter) / 8.208 + 7.3357 / self.Reynolds)
            A1 = self.Reynolds * (epsilon / self.diameter) + 9.3120665 * A0
            self.friction_coef = ((8.128943 + A1) / (8.128943 * A0 - 0.86859209 * A1 * math.log(A1 / (3.7099535 * self.Reynolds)))) ** 2
        else:
            self.friction_coef = 64 / self.Reynolds

        friction_loss = length * 8 * self.friction_coef * EA_density * (EA_consumption ** 2)  / (self.diameter ** 5 * math.pi ** 2)
        
        
        return friction_loss

    def weight_per_meter (self):
        return self.specific_mass