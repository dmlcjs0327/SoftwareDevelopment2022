import threading
from Tello import Tello

class TelloSender:

    def __init__(self, tello:Tello.Tello) -> None:
        self.__socket_cmd = tello.get_socket_cmd()
        self.__receiver = tello.get_receiver()
        self.__address = tello.get_address()
        self.__wait_time = tello.get_wait_time()
        self.__cancel_flag = None

        self.__send_lock = threading.Lock()
        
        
    

    #Tello에게 명령을 전송하는 함수
    def send_data(self,data:str) -> None:
        self.__send_lock.acquire()
        self.__cancel_flag = False
        timer = threading.Timer(self.__wait_time, self.set_cancel_flag)

        self.__socket_cmd.sendto(data, self.__address)

        timer.start()
        while self.__receiver.get_data() is None:
            if self.__cancel_flag is True:
                break
        timer.cancel()

        response = self.__receiver.get_data()
        self.__receiver.set_data(None)

        self.__send_lock.release()
        return response

    def set_cancel_flag(self):
        self.__cancel_flag = True

    