# import cv2
# import numpy as np

# # 웹캠 신호 받기
# class Yolo:
#     def __init__(self) -> None:
        
#         VideoSignal = cv2.VideoCapture(0)
#         # YOLO 가중치 파일과 CFG 파일 로드
#         YOLO_net = cv2.dnn.readNet("yolov2-tiny.weights","yolov2-tiny.cfg")

#         # YOLO NETWORK 재구성

#         classes = []  #객체 이름을 저장하는 배열
#         with open("yolo.names", "r") as f:   # 객체 이름들이 저장된 'yolo.names' open
#             classes = [line.strip() for line in f.readlines()]   # yolo.names 파일
#         layer_names = YOLO_net.getLayerNames()
#         output_layers = [layer_names[i[0] - 1] for i in YOLO_net.getUnconnectedOutLayers()]

#         while True:
#             # 웹캠 프레임
#             ret, frame = VideoSignal.read()
#             h, w, c = frame.shape

#             # YOLO 입력
#             blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0),
#             True, crop=False)
#             YOLO_net.setInput(blob)
#             outs = YOLO_net.forward(output_layers)

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




# import torch
# import cv2

# # Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s') 
# # model = torch.hub.load('ultralytics/yolov5', 'yolov5x6') 

# # Images
# #img = 'https://ultralytics.com/images/zidane.jpg'  # or file, Path, PIL, OpenCV, numpy, list
# # while True:
# cam = cv2.VideoCapture(0)
# ret, frame = cam.read()

# # Inference
# results = model(frame,augment = True)

# # Results
# results.crop()  # or .show(), .print(), .save(), .crop(), .pandas(), etc.
# print("test")


import torch
import numpy as np
import cv2
from time import time
import sys


class ObjectDetection:
    """
    The class performs generic object detection on a video file.
    It uses yolo5 pretrained model to make inferences and opencv2 to manage frames.
    Included Features:
    1. Reading and writing of video file using  Opencv2
    2. Using pretrained model to make inferences on frames.
    3. Use the inferences to plot boxes on objects along with labels.
    Upcoming Features:
    """
    def __init__(self, out_file="Labeled_Video.avi"):
        """
        :param input_file: provide youtube url which will act as input for the model.
        :param out_file: name of a existing file, or a new file in which to write the output.
        :return: void
        """
        self.model = self.load_model()
        self.model.conf = 0.4 # set inference threshold at 0.3
        self.model.iou = 0.3 # set inference IOU threshold at 0.3
        self.model.classes = [0] # set model to only detect "Person" class
        self.out_file = out_file
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def get_video_from_file(self):
        """
        Function creates a streaming object to read the video from the file frame by frame.
        :param self:  class object
        :return:  OpenCV object to stream video frame by frame.
        """
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        assert cap is not None
        return cap

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

    def __call__(self):
        player = self.get_video_from_file() # create streaming service for application
        assert player.isOpened()
        x_shape = int(player.get(cv2.CAP_PROP_FRAME_WIDTH))
        y_shape = int(player.get(cv2.CAP_PROP_FRAME_HEIGHT))
        four_cc = cv2.VideoWriter_fourcc(*"MJPG")
        out = cv2.VideoWriter(self.out_file, four_cc, 20, (x_shape, y_shape))
        fc = 0
        fps = 0
        tfc = int(player.get(cv2.CAP_PROP_FRAME_COUNT))
        tfcc = 0
        while True:
            fc += 1
            start_time = time()
            ret, frame = player.read()
            if not ret:
                break
            results = self.score_frame(frame)
            frame = self.plot_boxes(results, frame)
            end_time = time()
            fps += 1/np.round(end_time - start_time, 3)
            if fc == 10:
                fps = int(fps / 10)
                tfcc += fc
                fc = 0
                per_com = int(tfcc / tfc * 100)
                print(f"Frames Per Second : {fps} || Percentage Parsed : {per_com}")
            out.write(frame)
        player.release()


a = ObjectDetection()
a()