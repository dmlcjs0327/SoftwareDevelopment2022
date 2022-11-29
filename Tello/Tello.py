import threading
from Basemodel import Drone
import TelloController
import TelloMonocular
import TelloTOF
import TelloMotor
import TelloReceiver

class Tello(Drone):
    
    def __init__(self,stop_event:threading.Event) -> None:
        self.__stop_event = stop_event
        self.__controller = TelloController.TelloController()
        self.__monocular = TelloMonocular.TelloMonocular()
        self.__tof = TelloTOF.TelloTOF()
        self.__motor = TelloMotor.TelloMotor()
        self.__receiver = TelloReceiver()
        
        self.object_val = None
        self.tof_val = None
        self.window_coors = None
        self.queue = []

    def set_connection(self):
        pass
    
    def create_object_val(self):
        pass
    
    #Tello가 가진 object_val를 리턴
    def get_object_val(self):
        return self.object_val

    def set_tof_val():
        pass
    
    def set_window_coors():
        pass
    
    def insert_queue():
        pass
    
    def pop_queue():
        pass

    def get_stop_event(self):
        return self.__stop_event
    
    def get_receiver(self):
        return self.__receiver
    