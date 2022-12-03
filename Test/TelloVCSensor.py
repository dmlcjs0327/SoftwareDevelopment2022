from Basemodel.Sensor import Sensor
from CAD import Main
import threading
import sys



class TelloVCSensor(Sensor):
    """
    TelloVirtualController의 값을 받아오는 클래스
    """
    
    def __init__(self, main:Main):
        self.__stop_event = main.stop_event
        self.__virtual_controller = main.virtual_controller
        self.__planner = main.planner
        
        #스레드 실행
        self.__thr_sensor = threading.Thread(target=self.__func_sensor, daemon=True)
        self.__thr_sensor.start()
        


    #=====스레드에서 실행될 함수=====
    def __func_sensor(self):
        try:
            while not self.__stop_event.is_set():
                data = self.__take_data_from_sensor()
                info = self.__change_data_to_info(data)
                self.__save_to_planner(info)

        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)
        
        self.__printf("종료",sys._getframe().f_code.co_name)
    
    
    def __take_data_from_sensor(self): 
        """
        센서로부터 data를 가져온다
        """
        data:bytes = self.__virtual_controller.pop_controller_queue()
        return data
    
    
    def __change_data_to_info(self, data: bytes):
        """
        data를 Planner가 이해할 수 있는 info로 변경한다
        """
        info:str = data.decode('utf-8')
        return info
    
    
    def __save_to_planner(self, info: str):
        """
        info를 Planner에 저장한다
        """
        self.__planner.set_info_VSSensor(info)
    
    
    
    #=====실행내역 출력을 위한 함수=====
    #클래스명을 포함하여 출력하는 함수
    def __printc(self,msg:str):
        print("[{}] {}".format(self.__class__.__name__,msg))
    
    #클래스명 + 함수명을 출력하는 함수
    def __printf(self,msg:str,fname:str):
        self.__printc("[{}]: {}".format(fname, msg))