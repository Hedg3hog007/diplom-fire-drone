# DroneFireModel.py
from sqlalchemy import create_engine, Column, Integer, Float, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from db_module import get_db_path

Base = sqlalchemy.orm.declarative_base()

class DataBase_data:
      
    engine = create_engine(f"sqlite:///{get_db_path()}", echo=False)
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

    class BUILDINGS_specification(Base):
        __tablename__ = 'BUILDINGS_specification'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        lower_heat_value = Column(Integer)
        flame_spread = Column(Float)
        burnout_speed = Column(Float)
        fire_load_specific_mass = Column(Integer)
        heat_capacity = Column(Integer)

    def __init__(self):
        self._models = {
            'Дроны': self.UAV_specification,
            'Пожарные рукава': self.FIRE_HOSE_specification,
            'Огнетушащие вещества': self.EA_specification,
            'Помещения': self.BUILDINGS_specification
        }

    def record_get(self, tablename, id, attribute):
        model_class = self._models.get(tablename)
        if not model_class:
            print('Table ', tablename, ' not found')
            return "Table not found"
        
        record = self.session.query(model_class).filter_by(id = id).first()
        if record:
            return getattr(record, attribute)
        else:
            print ("Record ", tablename, 'id=', id, ' case=', attribute, " not found")
           
            
    def close_session(self):
        self.session.close()

    def add_record(self, tablename, **kwargs):
        model_class = self._models.get(tablename)
        if not model_class:
            print('Table ', tablename, ' not found')
            return None
        record = model_class(**kwargs)
        self.session.add(record)
        self.session.commit()
        return record

    def update_record(self, tablename, id, **kwargs):
        model_class = self._models.get(tablename)
        if not model_class:
            print('Table ', tablename, ' not found')
            return None
        record = self.session.query(model_class).filter_by(id=id).first()
        if not record:
            print('Record not found')
            return None
        for key, value in kwargs.items():
            setattr(record, key, value)
        self.session.commit()
        return record

    def delete_record(self, tablename, id):
        model_class = self._models.get(tablename)
        if not model_class:
            print('Table ', tablename, ' not found')
            return False
        record = self.session.query(model_class).filter_by(id=id).first()
        if not record:
            print('Record not found')
            return False
        self.session.delete(record)
        self.session.commit()
        return True
