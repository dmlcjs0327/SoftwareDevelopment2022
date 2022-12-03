from Basemodel.Actor import Actor
from CAD import Main

    
    
class TelloVGUIActor(Actor):
    
    def __init__(self, main:Main):
        self.__stop_event = main.stop_event
        self.__virtual_controller = main.virtual_controller
        self.__planner = main.planner


    def __take_cmd_from_planner(self): 
        """
        Planner로부터 cmd를 가져온다
        """
        pass
    
    
    def __change_cmd_for_drone(self):
        """
        cmd를 Drone이 이해할 수 있는 cmd로 변경한다
        """
        pass
    
    
    def __send_to_actuator(self):
        """
        cmd를 Actuator에게 전송한다
        """
        pass