# Fire_hose_model.py
import math

air_density = 1.293
g = 9.81

class Fire_hose:   

    def __init__ (self, fire_hose_diameter):
        self.diameter = fire_hose_diameter

    def gravitation_loss(EA_density, height):
        gravitation_loss  = (EA_density - air_density) * g * height
        return gravitation_loss
    
    def friction_loss (self, EA_density, EA_consumption, EA_viscosity, delta_height):

        Reynolds = (4 * EA_density * EA_consumption) / (math.pi * EA_viscosity * self.diameter)

        if Reynolds >= 4000:
            friction_coef = 0.3164 * (Reynolds ** 0.25)
        elif Reynolds <= 2300:
            friction_coef = 64 / Reynolds
        else:
            friction_coef = 64 / Reynolds * (1 - (Reynolds -2000)/2000) + 0.3164 * (Reynolds ** 0.25) * (Reynolds - 2000)/2000

        friction_loss = 8 * friction_coef * EA_consumption ** 2 * delta_height / (self.diameter ** 5 * math.pi ** 2 * g)
        return friction_loss
