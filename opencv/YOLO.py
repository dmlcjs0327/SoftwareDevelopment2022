import cv2
import numpy as np


# class Yolo:
#     def __init__(self,drone=None) -> None:
#         # YOLO 가중치 파일과 CFG 파일 로드
#         VideoSignal = cv2.VideoCapture(0)
#         self.YOLO_net = cv2.dnn.readNet("yolov2-tiny.weights","yolov2-tiny.cfg")

#         # YOLO NETWORK 재구성
#         self.classes = []  #객체 이름을 저장하는 배열

#         with open("yolo.names", "r") as f:   # 객체 이름들이 저장된 'yolo.names' open
#             classes = [line.strip() for line in f.readlines()]   # yolo.names 파일

#         layer_names = self.YOLO_net.getLayerNames()

#         output_layers = [layer_names[i[0] - 1] for i in self.YOLO_net.getUnconnectedOutLayers()]
#         print("YOLO 실행")

#         while True:
#             # 웹캠 프레임
#             if drone == None:
#                 ret, frame = VideoSignal.read()
#             else:
#                 frame = drone.frame
#             h, w, c = frame.shape

#             # YOLO 입력
#             blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0),True, crop=False)
#             self.YOLO_net.setInput(blob)
#             outs = self.YOLO_net.forward(output_layers)

#             class_ids = []
#             confidences = []
#             boxes = []

#             for out in outs:

#                 for detection in out:

#                     scores = detection[5:]
#                     class_id = np.argmax(scores)
#                     confidence = scores[class_id]

#                     if confidence > 0.5:
#                         # Object detected
#                         center_x = int(detection[0] * w)
#                         center_y = int(detection[1] * h)
#                         dw = int(detection[2] * w)
#                         dh = int(detection[3] * h)
#                         # Rectangle coordinate
#                         x = int(center_x - dw / 2)
#                         y = int(center_y - dh / 2)
#                         boxes.append([x, y, dw, dh])
#                         confidences.append(float(confidence))
#                         class_ids.append(class_id)

#             indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.45, 0.4)


#             for i in range(len(boxes)):
#                 if i in indexes:
#                     x, y, w, h = boxes[i]
#                     label = str(classes[class_ids[i]])
#                     score = confidences[i]

#                     # 경계상자와 클래스 정보 이미지에 입력
#                     cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 5)
#                     cv2.putText(frame, label, (x, y - 20), cv2.FONT_ITALIC, 0.5, 
#                     (255, 255, 255), 1)

#             cv2.imshow("YOLOv3", frame)

#             if cv2.waitKey(100) > 0:
#                 break


    
# if __name__ =="__main__":
#     Yolo()


import torch
import numpy as np
import cv2
from time import time,sleep
import sys
import threading
import platform
from PIL import Image, ImageTk
import tkinter

class ObjectDetection:

    def __init__(self,drone=None):
        """
        :param input_file: provide youtube url which will act as input for the model.
        :param out_file: name of a existing file, or a new file in which to write the output.
        :return: void
        """
        if not drone:
            self.drone = self
            self.cam = cv2.VideoCapture(0)
            self.root = tkinter.Tk()  # GUI 화면 객체 생성
            self.root.wm_title("TELLO Controller_TEST") #GUI 화면의 title 설정  
            self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose) #창을 나갈 경우에 대한 실행사항
            self.panel = None
            
        else:    
            print("YYYOOOO")
            self.drone = drone
            
        
        self.model = self.load_model()
        self.model.conf = 0.4 # set inference threshold at 0.3
        self.model.iou = 0.3 # set inference IOU threshold at 0.3
        self.model.classes = [0] # set model to only detect "Person" class
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.get_GUI_Image_thread = threading.Thread(target = self._getGUIImage, daemon=True)
        self.get_GUI_Image_thread.start() #이미지 편집 + 화면 이미지를 갱신하는 스레드
    
        if self.drone == self:
            self.root.mainloop()



    def _getGUIImage(self):
        
        system = platform.system()  #현재 운영체제 확인
        
        try:
            while True: #종료 상태가 아니면,
                frame = None
                
                if self.drone == self:
                    ret, frame = self.cam.read()
                else:
                    frame = self.drone.get_frame()
                if frame is None or frame.size == 0: 
                    continue #만약 받아온 frame이 없다면 pass
                

                start_time = time()
                results = self.score_frame(frame)
                frame = self.plot_boxes(results, frame)
                end_time = time()
                
                image = Image.fromarray(frame)  # frame을 이미지로 변환 

                if system =="Windows" or system =="Linux": 
                    self._updateGUIImage(image)
                    
                else: #mac OS의 경우 에러가 발생하는 것이 확인되어, 이를 방지하기 위해 새로운 thread로 실행
                    thread_tmp = threading.Thread(target=self._updateGUIImage,args=(image,))
                    thread_tmp.start()
                    time.sleep(0.03)    

        except Exception as e: print("[telloUI] _getGUIImage RuntimeError 발생: {}".format(e))
        print("[telloUI] _getGUIImage thread 종료")
                    
    
    # #화면을 새 frame으로 갱신하는 함수
    def _updateGUIImage(self,image):
        image = ImageTk.PhotoImage(image) #이미지를 imagetk 형식으로 변환

        if self.drone.panel is None: #panel이 없으면 생성
            self.drone.panel = tkinter.Label(image=image)
            self.drone.panel.image = image
            self.drone.panel.pack(side="left", padx=10, pady=10)
        
        else:
            self.drone.panel.configure(image=image)
            self.drone.panel.image = image

    def load_model(self):
        """
        Function loads the yolo5 model from PyTorch Hub.
        """
        model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
        return model

    def score_frame(self, frame):
        """
        function scores each frame of the video and returns results.
        :param frame: frame to be infered.
        :return: labels and coordinates of objects found.
        """
        self.model.to(self.device)
        results = self.model([frame])
        labels, cord = results.xyxyn[0][:, -1].to('cpu').numpy(), results.xyxyn[0][:, :-1].to('cpu').numpy()
        return labels, cord

    def plot_boxes(self, results, frame):
        """
        plots boxes and labels on frame.
        :param results: inferences made by model
        :param frame: frame on which to  make the plots
        :return: new frame with boxes and labels plotted.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]
        for i in range(n):
            row = cord[i]
            x1, y1, x2, y2 = int(row[0]*x_shape), int(row[1]*y_shape), int(row[2]*x_shape), int(row[3]*y_shape)
            bgr = (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 1)
            label = f"{int(row[4]*100)}"
            cv2.putText(frame, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            cv2.putText(frame, f"Total Targets: {n}", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame
    
    def onClose(self):
        self.stop_event.set() #종료를 알리는 버튼을 켜기
        self.root.quit() #화면 종료
        exit()

        
if __name__ == "__main__":
    test = ObjectDetection()
    
    
    
    
    
    
    
    
