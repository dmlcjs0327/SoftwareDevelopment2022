from abc import *

class Drone(metaclass=ABCMeta):
    monocular = None
    sensor = None
    controller = None
    motor = None
    
    @abstractmethod
    def set_connection(self):
        pass