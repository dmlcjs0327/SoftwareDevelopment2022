#완성
from abc import *
import numpy as np
from PIL import ImageTk



class ObjectDetector(metaclass=ABCMeta):
    
    @abstractmethod
    def __detect_from_frame(self, frame:np.fromstring)->tuple(ImageTk.PhotoImagey, tuple): 
        """
        frame에서 객체를 감지하고, 윈도우를 적용한 image 및 윈도우의 (좌상단좌표, 우하단좌표)좌표를 리턴 
        """
        pass