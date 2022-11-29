from Tello import Tello
from Tello import TelloReceiver
import tkinter
import threading
from time import sleep

class VirtualController:
    """
    가상의 컨트롤러를 의미하는 클래스
    -GUI 화면을 띄움
    -Tello의 ToF값을 화면에 출력
    -YOLO의 감지화면을 화면에 출력
    -키보드 및 화면의 버튼을 통해 Tello를 조작
    -thread_stay_connection 스레드를 통해 지속적으로 Tello에게 "command" 메세지를 전달
    -종료시 stop_event를 실행
    """



    #=====TestGUI의 인스턴스를 생성시 실행될 함수=====
    def __init__(self, tello:Tello) -> None:

        #TelloController 및 stop_event
        self.__receiver:TelloReceiver = tello.get_receiver()
        self.__stop_event:threading.Event = tello.get_stop_event()

        #Tello 조작시 동작범위
        self.__cm = 20
        self.__degree = 30

        #Tello에게 메세지 동시 전달을 방지하기 위한 lock
        self.__lock = threading.Lock()

        #화면 기본 설정
        self.__root = tkinter.Tk()  # GUI 화면 객체 생성
        self.__root.wm_title("CAD for Tello") #GUI 화면의 title 설정  
        self.__root.wm_protocol("WM_DELETE_WINDOW", self.__onClose) #종료버튼을 클릭시 실행할 함수 설정

        #화면에 띄울 문구 설정
        self.__text_tof = tkinter.Label(self.__root, text= "ToF: {} cm".format(self.tof), font='Helvetica 10 bold') ##re
        self.__text_tof.pack(side='top')

        self.__text_keyboard = tkinter.Label(self.__root, justify="left", text="""
        W - Move Tello Up\t\t\tArrow Up - Move Tello Forward
        S - Move Tello Down\t\t\tArrow Down - Move Tello Backward
        A - Rotate Tello Counter-Clockwise\t\tArrow Left - Move Tello Left
        D - Rotate Tello Clockwise\t\tArrow Right - Move Tello Right
        """)
        self.__text_keyboard.pack(side="top")

        #착륙 버튼
        self.__btn_landing = tkinter.Button(self.__root, text="Land", relief="raised", command=self.__land)
        self.__btn_landing.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)

        #이륙 버튼
        self.__btn_takeoff = tkinter.Button(self.__root, text="Takeoff", relief="raised", command=self.__takeoff)
        self.__btn_takeoff.pack(side="bottom", fill="both", expand="yes", padx=10, pady=5)

        #키보드 버튼들과 Tello 동작을 바인딩
        self.__keyboard_connection = tkinter.Frame(self.__root, width=100, height=2)
        self.__keyboard_connection.bind('<KeyPress-w>', self.__on_keypress_w)
        self.__keyboard_connection.bind('<KeyPress-s>', self.__on_keypress_s)
        self.__keyboard_connection.bind('<KeyPress-a>', self.__on_keypress_a)
        self.__keyboard_connection.bind('<KeyPress-d>', self.__on_keypress_d)
        self.__keyboard_connection.bind('<KeyPress-Up>', self.__on_keypress_up)
        self.__keyboard_connection.bind('<KeyPress-Down>', self.__on_keypress_down)
        self.__keyboard_connection.bind('<KeyPress-Left>', self.__on_keypress_left)
        self.__keyboard_connection.bind('<KeyPress-Right>', self.__on_keypress_right)
        self.__keyboard_connection.pack(side="bottom")
        self.__keyboard_connection.focus_set()

        self.__thread_stay_connection = threading.Thread(target=self.__func_stay_connection, daemon=True)
        self.__thread_stay_connection.start()

        self.__printn("시작")
        self.__root.mainloop()
    


    #=====실행내역 출력을 위한 함수=====
    def __printn(self,msg:str)->None:
        print("[{}] {}".format(self.__class__.__name__,msg))

    def __printm(self,key:str,action:str)->None:
        self.__printn("KEYBOARD {}: {} {} cm".format(key, action,self.__cm))

    def __printr(self,key:str,action:str)->None:
        self.__printn("KEYBOARD {}: {} {} degree".format(key, action,self.__degree))



    #=====버튼을 클릭했을 때 실행될 함수들=====
    def __land(self): #return: Tello의 receive 'OK' or 'FALSE'
        self.__send_cmd('land')

    def __takeoff(self): #return: Tello의 receive 'OK' or 'FALSE'
         self.__send_cmd('takeoff')



    #=====키보드를 입력했을 때 실행될 함수들=====
    def __on_keypress_w(self, event)->None:
        self.__printm("W","up")
        self.__move('up',self.__cm)

    def __on_keypress_s(self, event)->None:
        self.__printm("S","down")
        self.__move('down',self.__cm)

    def __on_keypress_a(self, event)->None:
        self.__printr("A","CCW")
        self.__rotate("ccw",self.__degree)

    def __on_keypress_d(self, event)->None:
        self.__printr("D","CW")
        self.__rotate("cw",self.__degree)

    def __on_keypress_up(self, event)->None:
        self.__printm("UP","forward")
        self.__move('forward',self.__cm)

    def __on_keypress_down(self, event)->None:
        self.__printm("DOWN","back")
        self.__move('back',self.__cm)

    def __on_keypress_left(self, event)->None:
        self.__printm("LEFT","left")
        self.__move('left',self.__cm)

    def __on_keypress_right(self, event)->None:
        self.__printm("RIGHT","right")
        self.__move('right',self.__cm)

    def __move(self, direction, distance)->None: 
        """
        direction: up, down, forward, back, right, left
        distance: 20~500 cm
        """
        self.__send_cmd("{} {}".format(direction, distance))
    
    def __rotate(self, direction, degree)->None:
        """
        direction: ccw, cw
        degree: 0~360 degree
        """
        self.__send_cmd("{} {}".format(direction, degree))



    #=====__thread_stay_connection에서 실행될 함수=====
    def __func_stay_connection(self):
        """
        Tello는 15초 이상 전달받은 명령이 없을시 자동 착륙하기 때문에,
        이를 방지하기 위해 5초 간격으로 Tello에게 "command" 명령을 전송
        """
        while not self.__stop_event.is_set():
            self.__send_cmd("command")
            sleep(5)
        


    #=====Tello에게 명령을 전송하는 함수=====
    def __send_cmd(self, msg:str)->str:
        self.__lock.acquire() #락 획득
        try:
            encoding_msg = msg.encode('utf-8')
            self.__receiver.insert_recv_queue(encoding_msg)
        except Exception as e:
            self.__printn(e)
        self.__lock.release() #락 해제



    #=====종료버튼을 클릭시 실행할 함수=====
    def __onClose(self):
        self.__stop_event.set() #stop_event를 실행
        self.__root.quit() #화면 종료
        self.__land() #텔로 착륙
        self.__printn("종료")
        exit()