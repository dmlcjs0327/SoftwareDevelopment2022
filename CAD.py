import threading
from Tello import Tello
from Plan import Planner
from Test import VirtualController

if __name__ == "__main__":
    stop_event = threading.Event()
    tello = Tello(stop_event)
    planner = Planner(tello)
    controller = VirtualController(tello)

    
    
    