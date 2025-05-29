# Fire_hose_model.py
import math
from DroneFireModel import DataBase_data

air_density = 1.293
g = 9.81

class Fire_hose:   
    db = DataBase_data()
    fire_hose_table = 'FIRE_HOSE_specification'

    def __init__ (self, fire_hose_init_id):
        self.fire_hose_id = fire_hose_init_id
        self.diameter = self.db.record_get(self.fire_hose_table, fire_hose_init_id, 'diameter')
        self.specific_mass = self.db.record_get(self.fire_hose_table, fire_hose_init_id, 'specific_mass')

    def gravitation_loss_per_meter(self, EA_density):
        gravitation_loss  = (EA_density - air_density) * g
        return gravitation_loss
    
    def friction_loss_per_meter (self, EA_density, EA_consumption, EA_viscosity):

        Reynolds = (4 * EA_density * EA_consumption) / (math.pi * EA_viscosity * self.diameter)

        if Reynolds > 1e5:
            friction_coef = 0.25 / ((math.log10((0.000025 / (3.7 * self.diameter)) + (5.74 / (Reynolds ** 0.9)))) ** 2)
        elif Reynolds >= 4000:
            friction_coef = 0.3164 / (Reynolds ** 0.25)
        elif Reynolds <= 2300:
            friction_coef = 64 / Reynolds
        else:
            friction_coef = (64 / Reynolds) * (1 - (Reynolds - 2000) / 2000) + (0.3164 / (Reynolds ** 0.25)) * ((Reynolds - 2000) / 2000)

        friction_loss = 8 * friction_coef * EA_density * (EA_consumption ** 2)  / (self.diameter ** 5 * math.pi ** 2)
        
        return friction_loss

    def weight_per_meter (self):
        return self.specific_mass