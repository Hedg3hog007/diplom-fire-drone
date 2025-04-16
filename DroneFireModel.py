# DroneFireModel.py
from sqlalchemy import create_engine, Column, Integer, Float, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy

Base = sqlalchemy.orm.declarative_base()

class DataBase_data:
      
    engine = create_engine('sqlite:///databases/DroneFireModel.db', echo = False)
    Session = sessionmaker(bind=engine)
    session = Session()

    class UAV_specification(Base):
        __tablename__ = 'UAV_specification'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        mass = Column(Integer)
        payload = Column(Integer)
        flight_time = Column(Integer)

    class FIRE_HOSE_specification(Base):
        __tablename__ = 'FIRE_HOSE_specification'
        id = Column(Integer, primary_key=True) 
        name = Column(String)
        diameter = Column(Float)
        pressure = Column(Integer)
        specific_mass = Column(Float)

    class EA_specification(Base):
        __tablename__ = 'EA_specification'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        heat_capacity = Column(Integer)
        density = Column(Integer)
        viscosity = Column(Integer)
        vaporation_capacity = Column(Integer)

    class BUILDINGS_specification(Base):
        __tablename__ = 'BUILDINGS_specification'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        fire_load = Column(Integer)
        lower_heat_value = Column(Integer)
        flame_spread = Column(Float)
        burnout_speed = Column(Float)
        fire_load_specific_mass = Column(Integer)
        coef_burn_completeness = Column(Float)

    def __init__(self):
        self._models = {
            'UAV_specification': self.UAV_specification,
            'FIRE_HOSE_specification': self.FIRE_HOSE_specification,
            'EA_specification': self.EA_specification,
            'BUILDINGS_specification': self.BUILDINGS_specification
        }

    def record_get(self, tablename, id, attribute):
        model_class = self._models.get(tablename)
        if not model_class:
            return "Table not found"
        
        record = self.session.query(model_class).filter_by(id = id).first()
        if record:
            return getattr(record, attribute)
        else:
            print ("Record not found")
            
            
        
    
    def close_session(self):
        self.session.close()


