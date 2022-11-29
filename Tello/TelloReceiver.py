import threading

class TelloReceiver:

    def __init__(self) -> None:
        self.__lock = threading.Lock()
        self.__recv_queue = []
    

    #recv_queue에 data를 삽입하는 함수
    def insert_recv_queue(self,data:str)->bool:
        self.__lock.acquire()
        self.__recv_queue.append(data)
        self.__lock.release()
    
    def pop_recv_queue(self)->str:
        self.__lock.acquire()
        if len(self.__recv_queue) == 0: 
            self.__lock.release()
            return None
        return_data = self.__recv_queue.pop(0)
        self.__lock.release()
        return return_data


    