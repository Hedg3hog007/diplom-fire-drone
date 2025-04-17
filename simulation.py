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
        UAV_record = self.db.record_get('UAV_specification', EA_id, 'name')
        building_record = self.db.record_get('BUILDINGS_specification', building_id, 'name')
        EA_record = self.db.record_get('EA_specification', EA_id, 'name')


        
        
        # симуляция ОТВ в пожарном рукаве. Вес, время тушения
        


        
        # симуляция пожара. Развитие, теплообмен с ОТВ

        