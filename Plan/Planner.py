import socket
import threading
import sys
from Calculation import ValueChanger
from Calculation import ValueChecker
from ObjectDetector.YOLOv2 import YOLOv2
from CAD import Main



class Planner:
    """
    연산을 담당하는 클래스
    1) 거리 정보, 윈도우 정보를 가져와서, 물체의 실제 크기를 계산
    2) 계산한 크기를 바탕으로 물체의 실제 크기에 대한 좌표값을 생성
    3) 생성한 좌표값을 바탕으로 회피궤적을 생성
    4) 회피궤적을 queue에 저장
    """
    
    
    
    #=====Planner의 인스턴스를 생성시 실행될 함수=====
    def __init__(self, main:Main):
        
        #Tello의 주소, 포트
        self.tello_address = ('192.168.10.1',8889) #텔로에게 접속했을 때, 텔로의 IP주소
        
        #종료를 위한 stop_event
        self.__stop_event = main.stop_event
        
        #각 센서가 저장하는 값
        self.__info_VSSensor = None #조종기의 명령
        self.__info_8889Sensor_tof = None #ToF
        self.__info_8889Sensor_cmd = None #수행확인명령
        self.__info_11111Sensor_frame = None #Frame
        self.__info_11111Sensor_image = None
        self.__info_11111Sensor_coor = None
        
        #객체감지를 위한 YOLOv2 객체
        self.__YOLOv2 = YOLOv2(self)
        
        #lock 생성
        self.__lock_info_VSSensor = threading.Lock()
        self.__lock_info_8889Sensor_tof = threading.Lock()
        self.__lock_info_8889Sensor_cmd = threading.Lock()
        self.__lock_info_11111Sensor_frame = threading.Lock()
        self.__lock_info_11111Sensor_image = threading.Lock()
        self.__lock_info_11111Sensor_coor = threading.Lock()
        
        #연결 정의
        self.socket8889 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4, UDP 통신 소켓 객체를 생성(command용)
        self.socket8889.bind(('', 8889)) #소켓 객체를 텔로와 바인딩(8889 포트)
        
        self.socket11111 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # IPv4, UDP 통신 소켓 객체를 생성(camera용)
        self.socket11111.bind(('', 11111)) #소켓 객체를 텔로와 바인딩(11111 포트)
        
        #스레드 실행
        self.__thr_planner = threading.Thread(target=self.__func_planner, daemon=True)
        self.__thr_planner.start()
                
                
                
    #=====스레드에서 실행될 함수=====
    def __func_planner(self):
        try:
            while not self.__stop_event.is_set():
                #1) frame 정보가 존재하면, YOLOv2를 통해 윈도우 좌표 list로 변경
                height, width = self.__create_window()
                
                #2) 장애물에 대한 실제 3차원 좌표 생성
                object_coor = self.__create_real_coor(height, width)
                
                #3) 3차원 좌표를 바탕으로 회피 명령 생성
                avd_cmd = self.__create_avd_cmd(object_coor)
                
                    
                    
                
                

        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)
        
        self.__printf("종료",sys._getframe().f_code.co_name)
    
    
    def __create_window(self):
        frame = self.get_info_11111Sensor_frame()
        if frame is not None: 
            height, width, c = frame.shape
            image, fusion_window = self.__YOLOv2.detect_from_frame(frame)
            self.set_info_11111Sensor_image(image)
            self.set_info_11111Sensor_coor(fusion_window)
            return None, None
        else:
            return (0,0)
    
    def __create_real_coor(self, height, width):
        tof = self.get_info_8889Sensor_tof()
        coor = self.get_info_11111Sensor_coor()
        object_val = (tof, coor, (height, width)) 
        object_coor = ValueChanger.change_val_to_coor(object_val)
        return object_coor
        
    #object_coor: (tof_val, real_center_coor, real_length)
    #입력값인 object_coor을 회피하는 명령인 avd_cmd를 생성
    def __create_avd_cmd(self,object_coor:tuple): 
        """
        -입력값 - object_coor: (tof값[cm], 물체중심의 가로좌표[cm], 물체중심의 세로좌표[cm], 물체의 가로길이[cm], 물체의 세로길이[cm])
        Tello의 SDK 명령으로 변환하는 함수는 Calculation 패키지의 ValueChanger.change_cmd_for_tello()가 있으므로
        리턴값은 원하는 형식대로 만들고, 이를 Tello SDK 명령어로 변환하는 ValueChanger.change_cmd_for_tello() 코드도 작성
        리턴: (이동방향, 해당 방향으로의 이동거리)
        """
        if object_coor is None:
            return None
        
        tof_val = object_coor[0]
        real_center_coor = object_coor[1]
        real_length = object_coor[2]
        

        
        
    
    
    
    #=====getter/setter 선언=====
    #VSSensor
    def get_info_VSSensor(self):
        self.__lock_info_VSSensor.acquire()
        info = self.__info_VSSensor
        self.__info_VSSensor = None
        self.__lock_info_VSSensor.release()
        return info
    
    def set_info_VSSensor(self, info):
        self.__lock_info_VSSensor.acquire()
        self.__info_VSSensor = info
        self.__lock_info_VSSensor.release()
        
    #8889Sensor_tof   
    def get_info_8889Sensor_tof(self):
        self.__lock_info_8889Sensor_tof.acquire()
        info = self.__info_8889Sensor_tof
        self.__info_8889Sensor_tof = None
        self.__lock_info_8889Sensor_tof.release()
        return info
    
    def set_info_8889Sensor_tof(self, info):
        self.__lock_info_8889Sensor_tof.acquire()
        self.__info_8889Sensor_tof = info
        self.__lock_info_8889Sensor_tof.release()
        
        
    #8889Sensor_cmd
    def get_info_8889Sensor_cmd(self):
        self.__lock_info_8889Sensor_cmd.acquire()
        info = self.__info_8889Sensor_cmd
        self.__info_8889Sensor_cmd = None
        self.__lock_info_8889Sensor_cmd.release()
        return info
    
    def set_info_8889Sensor_cmd(self, info):
        self.__lock_info_8889Sensor_cmd.acquire()
        self.__info_8889Sensor_cmd = info
        self.__lock_info_8889Sensor_cmd.release()
        
        
    #11111Sensor_frame    
    def get_info_11111Sensor_frame(self):
        self.__lock_info_11111Sensor_frame.acquire()
        info = self.__info_11111Sensor_frame
        self.__info_11111Sensor_frame = None
        self.__lock_info_11111Sensor_frame.release()
        return info
    
    def set_info_11111Sensor_frame(self, info):
        self.__lock_info_11111Sensor_frame.acquire()
        self.__info_11111Sensor_frame = info
        self.__lock_info_11111Sensor_frame.release()
    
    
    #11111Sensor_image    
    def get_info_11111Sensor_image(self):
        self.__lock_info_11111Sensor_image.acquire()
        info = self.__info_11111Sensor_image
        self.__info_11111Sensor_image = None
        self.__lock_info_11111Sensor_image.release()
        return info
    
    def set_info_11111Sensor_image(self, info):
        self.__lock_info_11111Sensor_image.acquire()
        self.__info_11111Sensor_image = info
        self.__lock_info_11111Sensor_image.release()
            
            
    #11111Sensor_coor
    def get_info_11111Sensor_coor(self):
        self.__lock_info_11111Sensor_coor.acquire()
        info = self.__info_11111Sensor_coor
        self.__info_11111Sensor_coor = None
        self.__lock_info_11111Sensor_coor.release()
        return info
    
    def set_info_11111Sensor_coor(self, info):
        self.__lock_info_11111Sensor_coor.acquire()
        self.__info_11111Sensor_coor = info
        self.__lock_info_11111Sensor_coor.release()   
    


    #=====실행내역 출력을 위한 함수=====
    #클래스명을 포함하여 출력하는 함수
    def __printc(self,msg:str):
        print("[{}] {}".format(self.__class__.__name__,msg))
    
    #클래스명 + 함수명을 출력하는 함수
    def __printf(self,msg:str,fname:str):
        self.__printc("[{}]: {}".format(fname, msg))
        
            