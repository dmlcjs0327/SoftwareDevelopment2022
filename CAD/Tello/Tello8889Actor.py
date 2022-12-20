#완성
from CAD.Basemodel.Actor import Actor
from CAD.Calculation import ValueChanger
from time import sleep
import threading
import sys
import traceback

    
class Tello8889Actor(Actor):
    """
    Tello 8889 port의 값을 받아오는 클래스
    """
    
    def __init__(self, main):
        self.__printc("생성")
        self.__stop_event = main.stop_event
        self.__main = main
        self.__tello_address = main.tello_address
        self.__planner = main.planner
        self.__socket = main.socket8889
        
        #스레드 실행
        self.__thr_actor = threading.Thread(target=self.__func_actor, daemon=True)
        self.__thr_actor.start()



    #=====스레드에서 실행될 함수=====
    def __func_actor(self):
        self.__printf("실행",sys._getframe().f_code.co_name)
        try:
            while not self.__stop_event.is_set() and not hasattr(self.__main, 'virtual_controller'):
                self.__printf("대기중",sys._getframe().f_code.co_name)
                sleep(1)
            
            self.__virtual_controller = self.__main.virtual_controller
            
            while not self.__stop_event.is_set():
                cmd = self.take_cmd_from_planner()
                if cmd is None: continue
                safe_cmd = self.change_cmd_is_safe(cmd)
                drone_cmd = self.change_cmd_for_drone(safe_cmd)
                self.send_to_actuator(drone_cmd)
                sleep(0.1)

        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)
            print(traceback.format_exc())
        
        self.__printf("종료",sys._getframe().f_code.co_name)
        
        #virtual controller 종료
        try:
            self.__virtual_controller.onClose()
        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)
            print(traceback.format_exc())


    def take_cmd_from_planner(self): 
        """
        Planner로부터 cmd를 가져온다
        """
        cmd = self.__planner.pop_cmd_queue()
        return cmd
    
    
    def change_cmd_is_safe(self, cmd): 
        """
        cmd가 충돌이 발생하지 않는 명령으로 변환한다
        """
        tof = self.__planner.get_info_8889Sensor_tof()
        threshold = self.__planner.threshold_distance
        safe_cmd = ValueChanger.change_to_safe_cmd(cmd, tof, threshold)
        return safe_cmd
    
    
    def change_cmd_for_drone(self, cmd):
        """
        cmd를 Drone이 이해할 수 있는 cmd로 변경한다
        """
        drone_cmd = ValueChanger.change_cmd_for_tello(cmd)
        return drone_cmd
    
    
    def send_to_actuator(self, cmd):
        """
        cmd를 Actuator에게 전송한다
        """
        if cmd is not None:
            #TEST
            if cmd.decode() != "EXT tof?":
                self.__printf("send: {}".format(cmd),sys._getframe().f_code.co_name)
            self.__socket.sendto(cmd, self.__tello_address)
    
    
    
    #=====실행내역 출력을 위한 함수=====
    #클래스명을 포함하여 출력하는 함수
    def __printc(self,msg:str):
        print("[{}] {}".format(self.__class__.__name__,msg))
    
    #클래스명 + 함수명을 출력하는 함수
    def __printf(self,msg:str,fname:str):
        self.__printc("[{}]: {}".format(fname, msg))