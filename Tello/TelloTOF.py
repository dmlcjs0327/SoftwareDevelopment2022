import threading
import socket
import sys
from Basemodel import Sensor
from Tello import Tello
from Calculation import ValueChecker



class TelloTOF(Sensor):
    """
    센서를 추상화한 클래스
    센서의 입력이 내부 큐에 저장되면, 입력을 꺼내 범위를 확인 후 드론에게 전송
    """
    
    #=====TelloTOF의 인스턴스를 생성시 실행될 함수=====
    def __init__(self, tello:Tello.Tello) -> None:
        self.__tello = tello
        self.__socket_cmd:socket.socket = tello.get_socket_cmd()
        self.__stop_event:threading.Event = tello.get_stop_event()
        self.__virtual_controller = tello.__virtual_controller

        self.__thread_tello_sensor = threading.Thread(target=self.__func_tello_sensor, daemon=True)
        self.__thread_tello_sensor.start()
    


    #=====스레드에서 실행될 함수=====
    def __func_tello_sensor(self) -> None:
        try:
            while not self.__stop_event.is_set():
                msg = self.__take_from_sensor()
                if msg is not None and self.__check_controller_value(msg):
                    self.__save_to_drone(msg)
        
        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)

    def __take_from_sensor(self) -> str or None: 
        if len(self.__virtual_controller) > 0:
            data:bytes = self.__virtual_controller.pop_controller_queue()
            if data is not None:
                msg = data.decode("utf-8")
                return msg
        return None
    
    def __check_sensor_value(self):
        pass
    
    def __save_to_drone(self):
        pass

    #=====실행내역 출력을 위한 함수=====
    #클래스명을 포함하여 출력하는 함수
    def __printc(self,msg:str)->None:
        print("[{}] {}".format(self.__class__.__name__,msg))
    
    #클래스명 + 함수명을 출력하는 함수
    def __printf(self,msg:str,fname:str)->None:
        self.__printc("[{}]: {}".format(fname, msg))
