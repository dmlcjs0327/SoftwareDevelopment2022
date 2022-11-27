from abc import *


class Monocular(metaclass=ABCMeta):
    
    """_summary_
    1) take_from_camera
    2) detect_object
    3) save_to_drone
    순으로 실행
    """
    
    @abstractmethod
    def take_from_camera(self): 
        pass
    
    @abstractmethod
    def detect_object(self):
        pass
    
    @abstractmethod
    def save_to_drone(self):
        pass
