from abc import *


class Drone(metaclass=ABCMeta):
    
    @abstractmethod
    def set_connection(self):
        pass
    
    @abstractmethod
    def create_object_val(self):
        pass
    
    @abstractmethod
    def get_object_val():
        pass

    @abstractmethod
    def set_tof_val():
        pass
    
    @abstractmethod
    def set_window_coors():
        pass
    
    @abstractmethod
    def insert_queue():
        pass
    
    @abstractmethod
    def pop_queue():
        pass
