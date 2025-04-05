# simulation_results.py
from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from EA_model import EA

Base = declarative_base()

class SimulationResult(Base):
    __tablename__ = 'simulation_results'
    id = Column(Integer, primary_key=True)
    amplitude = Column(Float)
    frequency = Column(Float)

class Database:
    def __init__(self, db_path='sqlite:///fire_model.db'):
        self.engine = create_engine(db_path, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def save_result(self, amplitude, frequency):
        session = self.Session()
        result = SimulationResult(amplitude=amplitude, frequency=frequency)
        session.add(result)
        session.commit()
        session.close()

    def EA_simulation_result(EA_id, hose_id):
        __tablename__ = 'EA_simulation_results'
        id = Column(Integer, primary_Key=True)
        height = Column(Integer)
        EA_consumption = Column(Float)
        EA_heat_capacity = Column(Float)

        
            
