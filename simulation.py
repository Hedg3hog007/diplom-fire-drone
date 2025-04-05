# simulation.py
# на вход ОТВ, БАС, высоту тушения, тип здания, площадь горения
# на выходе оптимальность, эффективность, подходит или нет, мощность пожаротушения

from EA_model import EA
from Fire_hose_model import Fire_hose
from UAV_model import UAV
from Fire_power_model import FireModel
from DroneFireModel import DataBase_data

class Simulation:
    db = DataBase_data()
    
    def simulation(self, UAV_id, building_id, EA_id, fire_height, fire_area):
        # получить данные о БАС, о здании, об ОТВ
        record = self.db.record_get('UAV_specification', 1, 'name')
        
        # симуляция ОТВ в пожарном рукаве. Вес, время тушения
        


        
        # симуляция пожара. Развитие, теплообмен с ОТВ


sim = Simulation()
sim.simulation(1, 1, 1, 100, 50)
        