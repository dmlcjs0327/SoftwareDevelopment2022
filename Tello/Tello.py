from Basemodel import Drone
import TelloController
import TelloMonocular
import TelloTOF
import TelloMotor

class Tello(Drone):
    
    def __init__(self) -> None:
        self.controller = TelloController.TelloController()
        self.monocular = TelloMonocular.TelloMonocular()
        self.tof = TelloTOF.TelloTOF()
        self.motor = TelloMotor.TelloMotor()
        
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