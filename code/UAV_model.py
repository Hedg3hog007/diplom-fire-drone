# UAV_model.py
import math

class UAV:

    def UAV_hose (FIRE_HOSE_diameter, FIRE_HOSE_mass_per_meter, height, EA_density):
        EA_mass = math.pi * FIRE_HOSE_diameter ** 2 / 4 * height * EA_density
        FIRE_HOSE_mass = FIRE_HOSE_mass_per_meter * height

    def UAV_reservoir (EA_volume, EA_density, height, UAV_flight_time):
        EA_mass = EA_volume * EA_density

        ## блок расчёта времени автономной работы 

