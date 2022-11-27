from Tello import Tello
from Calculation import ValueChanger
from Calculation import ValueChecker

class Planner:
    
    def __init__(self, tello:Tello) -> None:
        
        self.tello = tello
        self.object_val = tello.get_object_val()
        self.object_coor = ValueChanger.chagne_val_to_coor(self.object_val)
        
        self.avd_cmd = self.create_avd_cmd(self.object_coor)
        self.tello.insert_queue(self.avd_cmd)
        
        while len(tello.queue) > 0:
            cur_cmd = tello.pop_queue()
            if ValueChecker.is_safe_cmd(cur_cmd):
                tello.motor.set_send_cmd(cur_cmd)
            
            
    
    
    #object_coor: (tof값, (물체의 가로길이,물체의 세로길이), (물체 중점의 가로좌표, 물체 중점의 세로좌표)
    #입력값인 object_coor을 회피하는 명령인 avd_cmd를 생성
    def create_avd_cmd(self,object_coor:tuple)->str:
        pass
        
            