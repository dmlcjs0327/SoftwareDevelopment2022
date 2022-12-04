#완성
import socket
import threading
import sys
from time import sleep
from Calculation import ValueChanger
from ObjectDetector.YOLOv2 import YOLOv2
from CAD import Main



class Planner:
    """
    연산을 담당하는 클래스
    1) 거리 정보, 윈도우 정보를 가져와서, 물체의 실제 크기를 계산
    2) 계산한 크기를 바탕으로 물체의 실제 크기에 대한 좌표값을 생성
    3) 생성한 좌표값을 바탕으로 회피명령을 생성
    4) 회피명령을 queue에 저장
    """
    
    
    
    #=====Planner의 인스턴스를 생성시 실행될 함수=====
    def __init__(self, main:Main):
        
        #Tello의 주소, 포트
        self.tello_address = ('192.168.10.1',8889) #텔로에게 접속했을 때, 텔로의 IP주소
        
        #종료를 위한 stop_event
        self.__stop_event = main.stop_event
        
        #회피를 수행할 거리(cm)
        self.threshold_distance = 40
        
        #기본적으로 움직일 크기(cm)
        self.base_move_distance = 20
        
        #장애물 안전거리 보정치(cm) / Tello 지름의 절반보다 조금 큼
        self.safe_constant = 20
        
        #각 센서가 저장하는 값
        self.__cmd_queue = [] #명령을 저장할 큐
        self.__info_8889Sensor_tof = None #ToF
        self.__info_8889Sensor_cmd = None #수행확인명령
        self.__info_11111Sensor_frame = None #Frame
        self.__info_11111Sensor_image = None
        self.__info_11111Sensor_coor = None
        
        #객체감지를 위한 YOLOv2 객체
        self.__YOLOv2 = YOLOv2(self)
        
        #lock 생성
        self.__lock_cmd_queue = threading.Lock()
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
        
        self.__thr_stay_connection = threading.Thread(target=self.__func_stay_connection, daemon=True)
        self.__thr_stay_connection.start()
        
        self.__thr_requset_tof = threading.Thread(target=self.__func_request_tof, daemon=True)
        self.__thr_requset_tof.start()
                
                
                
    #=====스레드에서 실행될 함수=====
    #메인 스레드
    def __func_planner(self):
        try:
            while not self.__stop_event.is_set():
                #1) frame 정보가 존재하면, YOLOv2를 통해 윈도우 좌표 list로 변경
                height, width = self.__create_window()
                
                #2) 장애물에 대한 실제 3차원 좌표 생성
                object_coor = self.__create_real_coor(height, width)
                
                #3) 3차원 좌표를 바탕으로 회피 명령 생성
                avd_cmd = self.__create_avd_cmd(object_coor)
                
                #4) 생성한 명령을 queue에 저장
                self.insert_cmd_queue(avd_cmd)

        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)
        
        self.__printf("종료",sys._getframe().f_code.co_name)
    
    
    #Tello에게 15초 간격으로 command를 전송하는 함수
    def __func_stay_connection(self):
        """
        Tello는 15초 이상 전달받은 명령이 없을시 자동 착륙하기 때문에,
        이를 방지하기 위해 5초 간격으로 Tello에게 "command" 명령을 전송
        """
        try:
            while not self.__stop_event.is_set():
                self.insert_cmd_queue("command")
                sleep(5)

        except Exception as e:
            self.__printf("ERROR {}".format(e),sys._getframe().f_code.co_name)
        
        self.__printf("종료",sys._getframe().f_code.co_name)


    #Tello에게 15초 간격으로 command를 전송하는 함수
    def __func_request_tof(self):
        """
        Tello에게 0.1초 주기로 tof값 전송을 요청하는 스레드
        """
        try:
            while not self.__stop_event.is_set():
                self.insert_cmd_queue('EXT tof?')
                sleep(0.1)

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


    def __create_avd_cmd(self,object_coor:tuple): 
        """
        -입력값 - object_coor: (tof값[cm], 물체중심의 가로좌표[cm], 물체중심의 세로좌표[cm], 물체의 가로길이[cm], 물체의 세로길이[cm])
        -출력값 - avd_cmd: str (방향, 이동거리를 포함)
        """
        if object_coor is None or object_coor[0]>self.threshold_distance:
            return None
        
        tof_val = object_coor[0]
        real_center_coor = object_coor[1]
        real_length = object_coor[2]
        
        #계산된 회피거리를 저장할 변수
        horizontal_move = None
        vertical_move = None
        
        #물체의 좌표 + 텔로의 안전보정치 = 회피할 거리
        object_left_coor = real_center_coor[0] - real_length[0]//2 - self.safe_constant
        if object_left_coor < -100:
            object_left_coor = -100
        object_left_coor = -1*object_left_coor #크기비교를 위해 양수로 변환
            
        object_right_coor = real_center_coor[0] + real_length[0]//2 + self.safe_constant
        if object_right_coor > 100:
            object_right_coor = 100
        
        object_up_coor = real_center_coor[1] + real_length[1]//2 + self.safe_constant
        if object_up_coor > 100:
            object_up_coor = 100
        
        object_down_coor = real_center_coor[1] - real_length[1]//2 - self.safe_constant
        if object_down_coor < -100:
            object_down_coor = -100
        object_down_coor = -1*object_down_coor #크기비교를 위해 양수로 변환
        
        #어느 방향이 더 조금 움직여서 회피가 가능한지 계산
        if object_left_coor < object_right_coor:
            horizontal_move = -1 * object_left_coor
        else:
            horizontal_move = object_right_coor
            
        if abs(horizontal_move) == 100:
            horizontal_move = 0
        
            
        if object_down_coor < object_up_coor:
            vertical_move = -1 * object_down_coor
        else:
            vertical_move = object_up_coor
        
        if abs(vertical_move) == 100:
            vertical_move = 0
            
            
        #회피명령 생성 / 최소 움직임은 base_move_distance = 20cm
        avd_cmd = None
        
        if horizontal_move == 0 and vertical_move == 0:
            avoid_distance = self.threshold_distance - tof_val
            if avoid_distance < self.base_move_distance:
                avoid_distance = self.base_move_distance
                
            avd_cmd = "back {}".format(avoid_distance)
        
        elif horizontal_move == 0 and vertical_move != 0:
            if vertical_move < 0:
                if abs(vertical_move) < self.base_move_distance:
                    vertical_move = -1 * self.base_move_distance
                avd_cmd = "down {}".format(-1*vertical_move)
            
            else:
                if abs(vertical_move) < self.base_move_distance:
                    vertical_move = self.base_move_distance
                avd_cmd = "up {}".format(vertical_move)
        
        elif horizontal_move != 0 and vertical_move == 0:
            if horizontal_move < 0:
                if abs(horizontal_move) < self.base_move_distance:
                    horizontal_move = -1 * self.base_move_distance
                avd_cmd = "left {}".format(-1*horizontal_move)
            
            else:
                if abs(horizontal_move) < self.base_move_distance:
                    horizontal_move = self.base_move_distance
                avd_cmd = "right {}".format(horizontal_move)
        
        else:
            if abs(horizontal_move) < abs(vertical_move):
                if horizontal_move < 0:
                    if abs(horizontal_move) < self.base_move_distance:
                        horizontal_move = -1 * self.base_move_distance
                    avd_cmd = "left {}".format(-1*horizontal_move)
            
                else:
                    if abs(horizontal_move) < self.base_move_distance:
                        horizontal_move = self.base_move_distance
                    avd_cmd = "right {}".format(horizontal_move)
            
            else:
                if vertical_move < 0:
                    if abs(vertical_move) < self.base_move_distance:
                        vertical_move = -1 * self.base_move_distance
                    avd_cmd = "down {}".format(-1*vertical_move)
            
                else:
                    if abs(vertical_move) < self.base_move_distance:
                        vertical_move = self.base_move_distance
                    avd_cmd = "up {}".format(vertical_move)
        
        return avd_cmd

        
    
    #=====getter/setter 선언=====
    #cmd_queue
    def pop_cmd_queue(self):
        self.__lock_cmd_queue.acquire()
        info = self.__cmd_queue.pop(0)
        self.__lock_cmd_queue.release()
        return info
    
    def insert_cmd_queue(self, info):
        self.__lock_cmd_queue.acquire()
        self.__cmd_queue.append(info)
        self.__lock_cmd_queue.release()
        
    #8889Sensor_tof   
    def get_info_8889Sensor_tof(self):
        self.__lock_info_8889Sensor_tof.acquire()
        info = self.__info_8889Sensor_tof
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