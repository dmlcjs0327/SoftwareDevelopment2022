from Basemodel.Actor import Actor
from CAD import Main
import threading
import sys

    
class Tello8889Actor(Actor):
    """
    Tello 8889 port의 값을 받아오는 클래스
    """
    
    def __init__(self, main:Main):
        self.__stop_event = main.stop_event
        self.__planner = main.planner
        self.__thr_8889Actor = threading.Thread(target=self.__func_VCSensor, daemon=True)


    def __take_cmd_from_planner(self): 
        """
        Planner로부터 cmd를 가져온다
        """
        pass
    
    
    def __change_cmd_for_drone(self):
        """
        cmd를 Drone이 이해할 수 있는 cmd로 변경한다
        """
        pass
    
    
    def __send_to_actuator(self):
        """
        cmd를 Actuator에게 전송한다
        """
        pass
    
    
    
    #=====실행내역 출력을 위한 함수=====
    #클래스명을 포함하여 출력하는 함수
    def __printc(self,msg:str):
        print("[{}] {}".format(self.__class__.__name__,msg))
    
    #클래스명 + 함수명을 출력하는 함수
    def __printf(self,msg:str,fname:str):
        self.__printc("[{}]: {}".format(fname, msg))