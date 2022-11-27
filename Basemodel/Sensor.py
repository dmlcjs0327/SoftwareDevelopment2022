from abc import *


class Sensor(metaclass=ABCMeta):
    
    """_summary_
    1) take_from_sensor
    2) check_sensor_value
    3) save_to_drone
    순으로 실행
    """
    
    @abstractmethod
    def take_from_sensor(self): 
        pass
    
    @abstractmethod
    def check_sensor_value(self):
        pass
    
    @abstractmethod
    def save_to_drone(self):
        pass
