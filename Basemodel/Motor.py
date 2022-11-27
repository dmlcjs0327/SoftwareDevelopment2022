from abc import *


class Motor(metaclass=ABCMeta):
    
    @abstractmethod
    def pass_to_motor(self): 
        pass