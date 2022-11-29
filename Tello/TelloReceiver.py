import threading
import sys
from Tello import Tello

class TelloReceiver:

    def __init__(self, tello:Tello.Tello) -> None:
        self.__socket_cmd = tello.get_socket_cmd()
        self.__stop_event = tello.get_stop_event()
        
        self.__data = None
        self.__data_lock = threading.Lock()

        self.__thread_tello_receiver = threading.Thread(target=self.__func_tello_receiver, daemon=True)
        self.__thread_tello_receiver.start()
    

    #
    def __func_tello_receiver(self):
        try:
            while not self.__stop_event.is_set():
                data = self.__socket_cmd.recv(1024)
                self.set_data(data)

        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)



    #data에 접근하는 함수
    def get_data(self) -> bytes:
        self.__data_lock.acquire()
        data = self.__data
        self.__data_lock.release()
        return data
    
    def set_data(self, data:bytes) -> None:
        self.__data_lock.acquire()
        self.__data = data
        self.__data_lock.release()


    #=====실행내역 출력을 위한 함수=====
    #클래스명을 포함하여 출력하는 함수
    def __printc(self,msg:str)->None:
        print("[{}] {}".format(self.__class__.__name__,msg))
    
    #클래스명 + 함수명을 출력하는 함수
    def __printf(self,msg:str,fname:str)->None:
        self.__printc("[{}]: {}".format(fname, msg))