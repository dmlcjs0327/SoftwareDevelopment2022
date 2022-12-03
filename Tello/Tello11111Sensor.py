from Basemodel.Sensor import Sensor
from Decoder import H264decoder
from Decoder.h264_36 import h264decoder
from CAD import Main
import threading
import sys



class Tello11111Sensor(Sensor):
    
    #=====Tello11111Sensor의 인스턴스를 생성시 실행될 함수=====
    def __init__(self, main:Main):
        self.__stop_event = main.stop_event
        self.__planner = main.planner
        self.__socket = main.planner.socket11111
        self.__decoder = h264decoder.H264Decoder()
        self.__packet_data = bytes()
        
        #스레드 실행
        self.__thr_sensor = threading.Thread(target=self.__func_sensor, daemon=True)
        self.__thr_sensor.start()
    
    
    
    #=====스레드에서 실행될 함수=====
    def __func_sensor(self):
        try:
            while not self.__stop_event.is_set():
                packet_data = self.__take_data_from_sensor()
                self.__change_data_to_info(packet_data)

        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)
        
        self.__printf("종료",sys._getframe().f_code.co_name)
    
    
    def __take_data_from_sensor(self): 
        """
        센서로부터 data를 가져온다
        """
        data:bytes = self.__socket.recv(2048)
        self.__packet_data += data
        return self.__packet_data
    
    
    def __change_data_to_info(self, packet_data: bytes):
        """
        data를 Planner가 이해할 수 있는 info로 변경한다
        """
        if len(packet_data) != 1460: # frame의 끝이 아니면,
            for frame in H264decoder.decode(self.__decoder, packet_data): 
                self.__save_to_planner(frame)

            self.__packet_data = bytes()
    
    
    def __save_to_planner(self, info: str):
        """
        info를 Planner에 저장한다
        """
        self.__planner.set_info_11111Sensor(info)
    
    
    
    #=====실행내역 출력을 위한 함수=====
    #클래스명을 포함하여 출력하는 함수
    def __printc(self,msg:str):
        print("[{}] {}".format(self.__class__.__name__,msg))
    
    #클래스명 + 함수명을 출력하는 함수
    def __printf(self,msg:str,fname:str):
        self.__printc("[{}]: {}".format(fname, msg))

