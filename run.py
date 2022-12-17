#완성
import threading
import sys
from time import sleep
from CAD.Plan.Planner import Planner
from CAD.Tello.Tello8889Sensor import Tello8889Sensor
from CAD.Tello.Tello11111Sensor import Tello11111Sensor
from CAD.Test.TelloVCSensor import TelloVCSensor
from CAD.Tello.Tello8889Actor import Tello8889Actor
from CAD.Test.TelloVirtualController import TelloVirtualController


"""
- Architecture: Sense - Plan - Act Pattern

- 입력방식(유선, 무선 및 포트)에 따라 Sense 계열 클래스 생성
- 연산을 담당하는 Planner 클래스 생성
- 출력방식(유선, 무선 및 포트)에 따라 Act 계열 클래스 생성

- Sense 계열 클래스들은 
    1) 데이터를 가져오고
    2) 데이터를 Planner가 받아들일 수 있는 정보로 변경하고V2
    3) Planner에 저장
    
- Planner 클래스는
    1) 저장된 값을 원하는 정보로 가공(3차원 좌표값으로 변경)하고
    2) 가공한 정보를 바탕으로 회피 명령을 생성하고
    3) 생성된 명령을 Planner 내부에 저장
    
- Act 계열 클래스들은 
    1) Planner에 저장된 값을 가져와서
    2) Drone이 이해할 수 있는 값으로 변경하고
    2) Actuator로 전송

- 이 모든 과정은 순차적이 아닌 병렬적으로 수행(사용자 명령이 존재하기 때문)
"""

class Main:
    
    def __init__(self):
        print(">>> 프로그램 준비중...")
        self.stop_event = threading.Event()
        
        self.planner = Planner(self)
        sleep(0.2)
        
        self.tello8889sensor = Tello8889Sensor(self)
        self.tello11111sensor = Tello11111Sensor(self)
        
        self.tello8889actor = Tello8889Actor(self)
        
        self.virtual_controller = TelloVirtualController(self)
        self.telloVCsensor = TelloVCSensor(self)
    
    
    
if __name__ == "__main__":
    version = sys.version.split(".")
    if version[0] == "3" and version[1] == "6":
        Main()
    else:
        print(">>>파이썬 3.6만 지원됩니다.")
        print(">>>현재 버젼: {}".format(sys.version))