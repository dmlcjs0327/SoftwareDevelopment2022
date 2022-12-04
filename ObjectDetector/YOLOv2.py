#완성
from Basemodel.ObjectDetector import ObjectDetector
from Calculation import ValueChanger
from Plan.Planner import Planner
import numpy as np
from PIL import Image,ImageTk
import cv2



class YOLOv2(ObjectDetector):
    """
    객체인식을 담당하는 클래스
    """
    
    
    
    def __init__(self, planner:Planner):
        
        #planner 객체
        self.__planner = planner
        
        #weights, cfg 불러오기
        self.__YOLO_net = cv2.dnn.readNet("yolov2-tiny.weights","yolov2-tiny.cfg")
        
        #객체 이름을 불러와서 저장할 배열
        self.__classes = []  
        with open("yolo.names", "r") as f:   # 객체 이름들이 저장된 'yolo.names' open
            self.__classes = [line.strip() for line in f.readlines()]   # yolo.names 파일
        
        self.__layer_names = self.__YOLO_net.getLayerNames()
        self.__output_layers = [self.__layer_names[i[0] - 1] for i in self.__YOLO_net.getUnconnectedOutLayers()]
    
    
    
    
    def detect_from_frame(self, frame:np.fromstring)->tuple(ImageTk.PhotoImagey, list): 
        """
        frame에서 객체를 감지하고, 윈도우를 적용한 image 및 윈도우의 좌상단좌표, 우하단좌표가 담긴 list 리턴
        """
        
        if frame is None or frame.size == 0:
            return None
        
        height, width, c = frame.shape
        
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0),True, crop=False)
        self.__YOLO_net.setInput(blob)
        outs = self.__YOLO_net.forward(self.__output_layers)
        
        class_ids = []
        confidences = []
        boxes = []
        
        for out in outs:
            
            for detection in out:

                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.5:
                    # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    dw = int(detection[2] * width)
                    dh = int(detection[3] * height)
                    # Rectangle coordinate
                    x = int(center_x - dw / 2)
                    y = int(center_y - dh / 2)
                    boxes.append([x, y, dw, dh])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.45, 0.4)

        window_list = []
        #frame에 윈도우 적용
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.__classes[class_ids[i]])
                score = confidences[i]

                # 경계상자와 클래스 정보 이미지에 입력
                # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
                # cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5, (255, 255, 255), 1)
                window_list.append(((x,y),(x + w, y + h)))
        
        #IR window 그리기
        tof = self.__planner.get_info_8889Sensor_tof()
        window_left_up_coor, window_right_down_coor = self.__calculate_ir_window_coor(tof,height,width)
        cv2.rectangle(frame, window_left_up_coor, window_right_down_coor (0, 0, 255), 5)
        
        #IR 윈도우에 겹치는 윈도우 좌표 저장
        fusion_window = ValueChanger.change_windows_to_window(window_list,\
                                                              window_left_up_coor, window_right_down_coor,\
                                                              height, width)
        
        #frame을 image로 변환
        image = Image.fromarray(frame)  
        
        #image를 imagetk 형식으로 변환
        image = ImageTk.PhotoImage(image)
        
        return (image, fusion_window)
    
    
    def __calculate_ir_window_coor(self, tof, height, width):
        x = tof - 3
        
        screen_height = height
        screen_width = width
        
        window_left_up_coor_y = None
        window_right_down_coor_y = None
        
        window_left_up_coor_x = None
        window_right_down_coor_x = None
        
        #영상에서 ToF가 차지하는 세로 픽셀 길이 계산
        height_length_fov = 0.758 * x
        height_length_tof_start = 0.203 * x - 5.528
        height_length_tof_end = 0.555 * x - 4.472
        
        height_proportion_start = height_length_tof_start / height_length_fov
        height_proportion_end = height_length_tof_end / height_length_fov
        
        if height_proportion_start <= 0:
            window_left_up_coor_y = 0
        else:
            window_left_up_coor_y = int(height_proportion_start*screen_height)
        
        if height_proportion_end <= 0:
            window_right_down_coor_y = 0
        else:
            window_right_down_coor_y = int(height_proportion_start*screen_height)
        
        #영상에서 ToF가 차지하는 가로 픽셀 길이 계산
        width_length_fov = 1.048 * x
        width_length_tof_start = 0.348 * x - 0.528
        width_length_tof_end = 0.7 * x + 0.528
        
        width_proportion_start = width_length_tof_start / width_length_fov
        width_proportion_end = width_length_tof_end / width_length_fov
        
        if width_proportion_start <= 0:
            window_left_up_coor_x = 0
        else:
            window_left_up_coor_x = int(width_proportion_start*screen_width)
            
        if width_proportion_end <= 0:
            window_right_down_coor_x = 0
        else:
            window_right_down_coor_x = int(width_proportion_start*screen_width)
            
        window_left_up_coor = (window_left_up_coor_x, window_left_up_coor_y)
        window_right_down_coor = (window_right_down_coor_x, window_right_down_coor_y)
        
        return (window_left_up_coor, window_right_down_coor)