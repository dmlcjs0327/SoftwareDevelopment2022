import socket
import threading
from Basemodel import Drone
from Test import VirtualController
from Tello import TelloController
from Tello import TelloMonocular
from Tello import TelloTOF
from Tello import TelloMotor
from Tello import TelloReceiver
from Tello import TelloSender


class Tello(Drone):
    """
    드론을 추상화한 클래스
    따라서, 드론의 각 요소인 controller, monocular, tof, motor, receiver 클래스를 생성
    """


    #=====Tello의 인스턴스를 생성시 실행될 함수=====
    def __init__(self,stop_event:threading.Event) -> None:
        self.__address = ('192.168.10.1',8889)
        self.__wait_time = 3
        self.__stop_event = stop_event

        self.__object_val = None
        self.__tof_val = None
        self.__window_coors = None
        self.__queue = []
        self.__frame = None
        self.__image_YOLO = None

        self.__queue_lock = threading.Lock()
        self.__tof_val_lock = threading.Lock()
        self.__frame_lock = threading.Lock()
        self.__image_YOLO_lock = threading.Lock()
        
        self.__set_connection()
        self.__create_parts()
        self.__set_tello_state()
        
        
        

    #=====init에서 실행될 주요 함수=====
    #각 부품과의 통신방식을 설정
    def __set_connection(self):
        self.__socket_cmd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4, UDP 통신 소켓 객체를 생성(command용)
        self.__socket_cmd.bind(('', 8889)) #소켓 객체를 텔로와 바인딩(8889 포트)
        self.__socket_monocular = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4, UDP 통신 소켓 객체를 생성(camera용)
        self.__socket_monocular.bind(('', 11111)) #소켓 객체를 텔로와 바인딩(11111 포트)

    #각 부품을 생성 및 연결
    def __create_parts(self):
        self.__virtual_controller = VirtualController.VirtualController(self)
        self.__receiver = TelloReceiver.TelloReceiver(self)
        self.__sender = TelloSender.TelloSender(self)
        self.__controller = TelloController.TelloController(self)
        self.__monocular = TelloMonocular.TelloMonocular(self)
        self.__sensor = TelloTOF.TelloTOF(self)
        self.__motor = TelloMotor.TelloMotor(self)



    def __set_tello_state(self):
        self.send_command('command')   #SDK mode에 진입하도록 command 명령어를 전송
        self.send_command('streamon')  #동영상 스트림을 보내오도록 streamon 명령어를 전송
        self.send_command('speed 100') #Tello의 속도를 최대로 지정

    
    def create_object_val(self):
        pass
    
    #Tello가 가진 object_val를 리턴
    def get_address(self) -> tuple:
        return self.__address

    def get_wait_time(self) -> float:
        return self.__wait_time
    
    def get_object_val(self):
        return self.object_val

    def set_tof_val():
        pass
    
    def set_window_coors():
        pass

    def get_stop_event(self):
        return self.__stop_event
    
    def get_socket_monocular(self):
        return self.__socket_monocular

    def get_socket_cmd(self):
        return self.__socket_cmd

    def get_controller(self):
        return self.__controller

    def get_monocular(self):
        return self.__monocular

    def get_sensor(self):
        return self.__sensor

    def get_motor(self):
        return self.__motor

    def get_receiver(self):
        return self.__receiver 
    
    def get_sender(self):
        return self.__sender
    
    def get_virtual_controller(self):
        return self.__virtual_controller

    def get_tof_val(self):
        self.__tof_val_lock.acquire()
        tof_val = self.__tof_val
        self.__tof_val_lock.release()
        return tof_val
    
    def get_frame(self):
        self.__frame_lock.acquire()
        frame = self.__frame
        self.__frame_lock.release()
        return frame

    def get_image_YOLO(self):
        self.__image_YOLO_lock.acquire()
        image_YOLO = self.__image_YOLO
        self.__image_YOLO_lock.release()
        return image_YOLO

    #접근함수
    def insert_queue(self,data:str)->bool:
        self.__queue_lock.acquire()
        self.__queue.append(data)
        self.__queue_lock.release()
    
    def pop_queue(self)->str:
        self.__queue_lock.acquire()
        if len(self.__queue) == 0: 
            self.__queue_lock.release()
            return None
        return_data = self.__queue.pop(0)
        self.__queue_lock.release()
        return return_data
    