# Fire_hose_model.py
import math

air_density = 1.293
g = 9.81

class Fire_hose:   

    def __init__ (self, fire_hose_diameter, EA_density_init, EA_viscosity_init):
        self.diameter = fire_hose_diameter
        self.EA_density = EA_density_init
        self.EA_viscosity = EA_viscosity_init

    def gravitation_loss_per_meter(self):
        gravitation_loss  = (self.EA_density - air_density) * g
        return gravitation_loss
    
    def friction_loss_per_meter (self, EA_consumption):

        Reynolds = (4 * self.EA_density * EA_consumption) / (math.pi * self.EA_viscosity * self.diameter)

        if Reynolds >= 4000:
            friction_coef = 0.3164 * (Reynolds ** 0.25)
        elif Reynolds <= 2300:
            friction_coef = 64 / Reynolds
        else:
            friction_coef = 64 / Reynolds * (1 - (Reynolds - 2000) / 2000) + 0.3164 * (Reynolds ** 0.25) * (Reynolds - 2000) / 2000

        friction_loss = 8 * friction_coef * EA_consumption ** 2  / (self.diameter ** 5 * math.pi ** 2 * g)
        
        return friction_loss


